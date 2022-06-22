import os
import math
import random
import hashlib
import caching
import psycopg2
import requests

from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from config import MINIMUM_BACKGROUND_BRIGHTNESS, CACHE_DIR, FONT_LOCATION
from utils import remove_sp_symbols, replace_sp_symbols, remove_multiplying_symbols

__author__ = 'Yegor Yershov'

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
	else:
		text = name[0][0] + name[1][0]

	text = text.upper()

	img = Image.new("RGBA", (width, height), color=main_background)
	draw = ImageDraw.Draw(img)
	draw.ellipse((0, 0, width, height), fill = color, outline = color)
	fnt = ImageFont.truetype(FONT_LOCATION, max(12, min(width, height)//2))
	w, h = draw.textsize(text, font=fnt)
	draw.text(((width-w)/2,(height-h)/2), text, fill='white', font=fnt)

	return img

def make_request(url, is_default=False): # is_default means if we are trying to get image from ui avatar generator
	response = requests.get(url)
	error_string = f"Url response code, image expected from is {response.status_code}."

	assert response.status_code == 200, error_string
	return response.content

def make_photo(database, size=64, background='random', name=None, url=None, chat_id=None, user_id=None, 
													client='web', push=False, main_background=None, theme='light'):
	size = size.split('x')
	if len(size) == 1:
		size = (max(16, min(512, int(size[0]))), max(16, min(512, int(size[0]))))
	else:
		size = (max(16, min(512, int(size[0]))), max(16, min(512, int(size[1]))))

	if user_id or chat_id:
		if user_id:
			database.execute('SELECT nickname, avatar_url FROM users WHERE user_id = {}'.format(user_id))
		elif chat_id:
			database.execute('SELECT name, avatar_url FROM chat WHERE chat_id = {}'.format(chat_id))
		obj = database.fetchone()

		if not url:
			url = obj[1]
		if not name:
			name = obj[0]

	if url:
		filename = f"{url.split('/')[-1]}_{client}"
		filename = hashlib.shake_128(filename.encode('utf-8')).hexdigest(length=12)
		info = [size, push]

		if caching.is_cached(filename=filename, info=info):
			img = Image.open(f'{CACHE_DIR}/{filename}.png')
		else:
			content = make_request(url)
			img = Image.open(BytesIO(content))
			img.thumbnail(size, Image.ANTIALIAS)
			caching.cache(img, filename=filename, info=info)
	else:
		filename = f"{name}_{client}"
		filename = hashlib.shake_128(filename.encode('utf-8')).hexdigest(length=12)
		info = [size, background, main_background, theme, push]

		if caching.is_cached(filename=filename, info=info):
			img = Image.open(f'{CACHE_DIR}/{filename}.png')
		else:
			img = draw_name(name, width=size[0], height=size[1], background=background, main_background=main_background, theme=theme)
			caching.cache(img, filename=filename, info=info)

	#img.save('res.png', 'PNG')

	img_byte_arr = BytesIO()
	img.save(img_byte_arr, format='PNG')

	return img_byte_arr.getvalue()