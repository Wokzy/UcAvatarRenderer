import os
import math
import grpc
import random
import base64
import hashlib
import caching
import psycopg2
import requests

import group_pb2
import group_pb2_grpc
import user_data_store_pb2
import uc_types_pb2 as uc_types
import user_data_store_pb2_grpc as user_data

from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, UnidentifiedImageError, ImageOps
from utils import remove_sp_symbols, replace_sp_symbols, remove_multiplying_symbols
from config import MINIMUM_BACKGROUND_BRIGHTNESS, CACHE_DIR, FONT_LOCATION, PUSH_IMAGE_TYPE, PUSH_IMAGE_LOCATION, PUSH_IMAGE_DIVISOR, SVG_REQUIRED_PACKAGE

__author__ = 'Yegor Yershov'

global svg_lib_usage
svg_lib_usage = None

class ColorGenerator:
	def __init__(self):
		pass

	def generate(self, name, theme='light'):
		self.hash_code(name)
		hue = self.generate_hue(self.hash)
		saturation = self.generate_saturation(theme)/100
		lightness = self.generate_lightness(theme)/100

		return (hue, saturation, lightness)

	def generate_hue(self, value):
		return self.scaleRange(value & 0xffff, {'min': 0, 'max': 0xffff}, {'min': 0, 'max': 360})

	def scaleRange(self, value, origin, target):
		scaled = ((value - origin['min']) * (target['max'] - target['min'])) / (origin['max'] - origin['min']) + target['min']
		return math.floor(scaled)

	def generate_saturation(self, theme):
		match theme:
			case 'light':
				return 55
			case 'dark':
				return 50

	def generate_lightness(self, theme):
		match theme:
			case 'light':
				return 65
			case 'dark':
				return 60

	def hash_code(self, text):
		self.hash = 0
		for i in range(len(text)):
			self.hash = ord(text[i]) + ((self.hash << 5) - self.hash)
			self.hash = self.hash & self.hash


def hsv_to_rgb(h, s, v):
	c = v*s
	x = c * (1 - abs((h/60) % 2 - 1))
	m = v - c

	if 0 <= h < 60: rgb = (c, x, 0)
	elif 60 <= h < 120: rgb = (x, c, 0)
	elif 120 <= h < 180: rgb = (0, c, x)
	elif 180 <= h < 240: rgb = (0, x, c)
	elif 240 <= h < 300: rgb = (x, 0, c)
	elif 300 <= h <= 360: rgb = (c, 0, x)

	r = (rgb[0]+m)*255
	g = (rgb[1]+m)*255
	b = (rgb[2]+m)*255

	return r, g, b

def hsv2rgb(h, s, v):
	return tuple([int(i) for i in hsv_to_rgb(h, s, v)])

def color_transform(clr, name=None, theme='light'):
	if clr == 'random':
		if not name:
			color = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
		else:
			color = ColorGenerator().generate(name, theme=theme)
			color = hsv2rgb(color[0], color[1], color[2])
	elif clr != None and len(clr.split(',')) > 1:
			color = tuple([min(max(1, int(i)), 255) for i in clr.split(',')])
			color = hsv2rgb(color[0], color[1], color[2])
	else:
		color = clr

	return color

def draw_name(name, width=None, height=None, background='random', main_background=None, theme='light'):
	if not width:
		if not height:
			height = 256
		width = height
	elif not height:
		height = width

	color = color_transform(background, name, theme=theme)
	if main_background != None:
		if ',' in main_background:
			main_background = tuple([int(i) for i in main_background.split(',')])

	name = remove_sp_symbols(name)
	name = remove_multiplying_symbols(name.strip())
	name = list(filter(('').__ne__, name.split(' ')))
	if len(name) == 1:
		text = name[0][0]
		if len(name[0]) > 1:
			text += name[0][1]
	else:
		text = name[0][0] + name[1][0]

	text = text.upper()

	img = Image.new("RGBA", (width, height), color=main_background)
	draw = ImageDraw.Draw(img)
	draw.ellipse((0, 0, width, height), fill = color)
	fnt = ImageFont.truetype(FONT_LOCATION, max(12, min(width, height)//2))
	w, h = draw.textsize(text, font=fnt)
	draw.text(((width-w)/2,(height-h)/2), text, fill='white', font=fnt)

	return img

def make_request(url, is_default=False): # is_default means if we are trying to get image from ui avatar generator
	response = requests.get(url)
	error_string = f"Url response code, image expected from is {response.status_code}."

	assert response.status_code == 200, error_string
	return response.content

def make_circle_avatar(img, size):
	mask = Image.new('L', size, 0)
	draw = ImageDraw.Draw(mask)
	draw.ellipse((0, 0) + size, fill = 255)

	output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
	output.putalpha(mask)

	return output #Image.alpha_composite(img, output)

def load_image_from_url(url):
	global svg_lib_usage

	if 'data:image' in url and 'base64' in url:
		img = Image.open(BytesIO(base64.b64decode(url.split(',')[-1].replace(' ', '+'))))
	else:
		content = make_request(url)
		try:
			img = Image.open(BytesIO(content))
		except UnidentifiedImageError:
			'''
			out = BytesIO()
			cairosvg.svg2png(url=url, write_to=out)
			img = Image.open(out)
			'''
			if not svg_lib_usage:
				return "The format of image you want to load is svg, which was disabled manually."
			with svg_lib_usage.Image(blob=content, format="svg") as image:
				png_image = image.make_blob("png")
			img = Image.open(BytesIO(png_image))

	return img

def add_push_part(img, size):
	rsize = (size[0] // PUSH_IMAGE_DIVISOR, size[1] // PUSH_IMAGE_DIVISOR)
	offset = (size[0] - rsize[0], size[1] - rsize[1])

	composite_img = Image.new("RGBA", size)

	if PUSH_IMAGE_TYPE == 'local':
		push = Image.open(PUSH_IMAGE_LOCATION).resize(rsize, Image.ANTIALIAS)
	else:
		push = load_image_from_url(PUSH_IMAGE_LOCATION).resize(rsize, Image.ANTIALIAS)

	composite_img.paste(push, offset)

	return Image.alpha_composite(img, composite_img)

def make_photo(user_channel, chat_channel, size="64", background='random', name=None, url=None, chat_id=None, user_id=None, svg = True,
												client='web', push=False, main_background=None, theme='light', etag = None):
	global svg_lib_usage
	if svg:
		import wand.image
		svg_lib_usage = wand.image

	size = size.split('x')
	if len(size) == 1:
		size = (max(16, min(512, int(size[0]))), max(16, min(512, int(size[0]))))
	else:
		size = (max(16, min(512, int(size[0]))), max(16, min(512, int(size[1]))))

	if user_id or chat_id:
		if user_id:
			info = user_data_store_pb2.GetUserInfoRequest(user_id=int(user_id))
			stupgr = user_data.UserDataStoreServiceStub(user_channel)
			res = stupgr.get_user_info(info)
			if not name:
				try:
					name = res.info.nickname
				except:
					pass
		elif chat_id:
			info = uc_types.GroupChatInfoRequest(group_id=int(chat_id), with_members=False)
			stupgr = group_pb2_grpc.GroupChatServiceStub(chat_channel)
			res = stupgr.get_info(info)
			if not name:
				try:
					name = res.info.name
				except:
					pass
		if not url:
			try:
				url = res.info.avatar_url
			except:
				pass

	if url:
		filename = f"{url.split('/')[-1]}_{client}"
		filename = hashlib.shake_128(filename.encode('utf-8')).hexdigest(length=12)
		info = [size, push]

		if caching.is_cached(filename=filename, info=info):
			img = Image.open(f'{CACHE_DIR}/{filename}.png')
			if caching.check_etag(img, etag):
				return 304, 'ETag matches'
		else:
			img = load_image_from_url(url)
			if img != None and img.__class__.__name__ != 'str':
				img = make_circle_avatar(img.resize(size, Image.ANTIALIAS), size)
			else:
				return 400, img
			if push and str(push).lower() == 'true':
				img = add_push_part(img, size)
			caching.cache(img, filename=filename, info=info)
	elif name:
		filename = f"{name}_{client}"
		filename = hashlib.shake_128(filename.encode('utf-8')).hexdigest(length=12)
		info = [size, background, main_background, theme, push]

		if caching.is_cached(filename=filename, info=info):
			img = Image.open(f'{CACHE_DIR}/{filename}.png')
			if caching.check_etag(img, etag):
				return 304, 'ETag matches'
		else:
			img = draw_name(name, width=size[0], height=size[1], background=background, main_background=main_background, theme=theme)
			if push and str(push).lower() == 'true':
				img = add_push_part(img, size)
			caching.cache(img, filename=filename, info=info)
	else:
		return 400, 'No name and avatar url, smth got wrong'

	#img.save('res.png', 'PNG')

	img_byte_arr = BytesIO()
	img.save(img_byte_arr, format='PNG')

	return img_byte_arr.getvalue(), caching.generate_entag(img)