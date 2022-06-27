# Config file for renderer

import json

file = open('config.json')
cfg = json.load(file)
file.close()

SERVICE_HOST = cfg['SERVICE_HOST']
SERVICE_PORT = cfg['SERVICE_PORT']

DATABASE_HOST = cfg['DATABASE_HOST']
DATABASE_NAME = cfg['DATABASE_NAME']
DATABASE_USER = cfg['DATABASE_USER']
DATABASE_PASSWORD = cfg['DATABASE_PASSWORD']

MINIMUM_BACKGROUND_BRIGHTNESS = cfg['MINIMUM_BACKGROUND_BRIGHTNESS'] # Minimal brightness to switch text color from black into while
CACHE_DIR = cfg['CACHE_DIR']
CACHE_EXPIRATION_TIME = cfg['CACHE_EXPIRATION_TIME'] # In seconds

FONT_LOCATION = cfg['FONT_LOCATION']
PUSH_IMAGE_TYPE = cfg['PUSH_IMAGE_TYPE'] # local/url
PUSH_IMAGE_LOCATION = cfg['PUSH_IMAGE_LOCATION']
PUSH_IMAGE_DIVISOR = cfg['PUSH_IMAGE_SIZE_DIVISOR']

SVG_REQUIRED_PACKAGE = 'libmagickwand-dev'