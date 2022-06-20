import os
import random
import caching
import psycopg2
import requests

from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from config import MINIMUM_BACKGROUND_BRIGHTNESS, CACHE_DIR

__author__ = 'Yegor Yershov'

def draw_name(name, width=None, height=None, background='random'):
	if not width:
		if not height:
			height = 256
		width = height
	elif not height:
		height = width

	if background == 'random':
		color = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
	elif len(background.split(',')) > 1:
			color = tuple([min(max(1, int(i)), 255) for i in background.split(',')])
	else:
		color = background

	if color.__class__.__name__ == 'str' and color == 'black':
		text_color = 'white'
	elif color.__class__.__name__ == 'tuple' and color[0] < MINIMUM_BACKGROUND_BRIGHTNESS and color[1] < MINIMUM_BACKGROUND_BRIGHTNESS and color[2] < MINIMUM_BACKGROUND_BRIGHTNESS:
		text_color = 'white'
	else:
		text_color = 'black'
	name = name.split(' ')
	if len(name) == 1:
		text = name[0][0]
	else:
		text = name[0][0] + name[-1][0]

	img = Image.new("RGBA", (width, height), color=color)
	draw = ImageDraw.Draw(img)
	fnt = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu/Ubuntu-M.ttf', max(12, min(width, height)//2))
	w, h = draw.textsize(text, font=fnt)
	draw.text(((width-w)/2,(height-h)/2), text, fill=text_color, font=fnt)

	return img

def make_request(url, is_default=False): # is_default means if we are trying to get image from ui avatar generator
	response = requests.get(url)
	error_string = f"Url response code, image expected from is {response.status_code}."

	assert response.status_code == 200, error_string
	return response.content

def make_photo(database, size=64, background='random', name=None, url=None, chat_id=None, user_id=None, client='web', push=False):
	size = size.split('x')
	if len(size) == 1:
		size = (max(16, min(512, int(size[0]))), max(16, min(512, int(size[0]))))
	else:
		size = (max(16, min(512, int(size[0]))), max(16, min(512, int(size[1]))))

	if user_id or chat_id:
		if user_id:
			database.execute('SELECT * FROM users WHERE user_id = {}'.format(user_id))
		elif chat_id:
			database.execute('SELECT * FROM chat WHERE chat_id = {}'.format(chat_id))
		obj = database.fetchone()

		if not url:
			url = obj[6]
		if not name:
			name = obj[2]

	if url:
		filename = f"{url}_{client}"
		if caching.is_cached(filename=filename, info=[size]):
			img = Image.open(f'{CACHE_DIR}/{filename}.png')
		else:
			content = make_request(url)
			img = Image.open(BytesIO(content))
			img.thumbnail(size, Image.ANTIALIAS)
			caching.cache(img, filename=filename, info=[size])
	else:
		filename = f"{name}_{client}"
		if caching.is_cached(filename=filename, info=[size, background]):
			img = Image.open(f'{CACHE_DIR}/{filename}.png')
		else:
			img = draw_name(name, width=size[0], height=size[1], background=background)
			caching.cache(img, filename=filename, info=[size, background])

	#img.save('res.png', 'PNG')

	img_byte_arr = BytesIO()
	img.save(img_byte_arr, format='PNG')

	return img_byte_arr.getvalue()