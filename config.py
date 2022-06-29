# Config file for renderer

import json

file = open('config.json')
cfg = json.load(file)
file.close()

SERVICE_HOST = cfg['SERVICE_HOST']
SERVICE_PORT = cfg['SERVICE_PORT']

GRPC_HOST = cfg['GRPC_HOST']
GRPC_DATABASE_PORT = cfg['GRPC_DATABASE_PORT']
GRPC_GROUPSERVICE_PORT = cfg['GRPC_GROUPSERVICE_PORT']

MINIMUM_BACKGROUND_BRIGHTNESS = cfg['MINIMUM_BACKGROUND_BRIGHTNESS'] # Minimal brightness to switch text color from black into while
CACHE_DIR = cfg['CACHE_DIR']
CACHE_EXPIRATION_TIME = cfg['CACHE_EXPIRATION_TIME'] # In seconds

FONT_LOCATION = cfg['FONT_LOCATION']
PUSH_IMAGE_TYPE = cfg['PUSH_IMAGE_TYPE'] # local/url
PUSH_IMAGE_LOCATION = cfg['PUSH_IMAGE_LOCATION']
PUSH_IMAGE_DIVISOR = cfg['PUSH_IMAGE_SIZE_DIVISOR']

SVG_REQUIRED_PACKAGE = 'libmagickwand-dev'