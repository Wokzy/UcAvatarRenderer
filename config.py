# Config file for renderer

SERVICE_HOST = ''
SERVICE_PORT = 8000

DATABASE_HOST = ''
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''

MINIMUM_BACKGROUND_BRIGHTNESS = 160 # Minimal brightness to switch text color from black into while
CACHE_DIR = 'cached_photo'
CACHE_EXPIRATION_TIME = 3600*5 # In seconds (5 hour)

FONT_LOCATION = '' #'/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf'
PUSH_IMAGE_TYPE = 'local' # local/url
PUSH_IMAGE_LOCATION = './push_image.png'
PUSH_IMAGE_DIVISOR = 3