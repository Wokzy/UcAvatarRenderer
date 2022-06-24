import os
import time
import pickle
import hashlib

from io import BytesIO
from datetime import datetime
from config import CACHE_DIR, CACHE_EXPIRATION_TIME

def cache(img, filename, info):
	img.save(f"{CACHE_DIR}/{filename}.png", format="PNG")

	with open(f'{CACHE_DIR}/{filename}.bin', 'wb') as f:
		data = (datetime.now(), CACHE_EXPIRATION_TIME, info)
		pickle.dump(data, f)
		f.close()

def is_cached(filename, info):
	if f'{filename}.bin' not in os.listdir(CACHE_DIR):
		return False

	with open(f'{CACHE_DIR}/{filename}.bin', 'rb') as f:
		data = pickle.load(f)
		f.close()

	if data[2] == info:
		return True
	return False

def check_expiration(filename):
	with open(f'{CACHE_DIR}/{filename}.bin', 'rb') as f:
		data = pickle.load(f)
		f.close()

	if (datetime.now() - data[0]).total_seconds() >= data[1]:
		os.remove(f'{CACHE_DIR}/{filename}.bin')
		os.remove(f'{CACHE_DIR}/{filename}.png')

def check_expiration_thread():
	if CACHE_DIR not in os.listdir():
		os.mkdir(CACHE_DIR)

	while True:
		for file in os.listdir(CACHE_DIR):
			if file.split('.')[-1] == 'bin':
				check_expiration(file.replace('.bin', ''))

		time.sleep(3)

def generate_entag(img):
	out = BytesIO()
	img.save(out, 'PNG')
	etag = hashlib.sha256(out.getvalue()).hexdigest()

	return etag

def check_etag(img, etag):
	return etag == generate_entag(img)
