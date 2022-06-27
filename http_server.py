import io
import caching
import renderer
import psycopg2
import threading

from config import *
from PIL import Image
from flask import Flask, jsonify, request, Response

__author__ = 'Yegor Yershov'

global cursor, conn, database_usage, debug_mode, svg_lib_usage
favicon_loaded = False
cursor = False
conn = None
database_usage = True
debug_mode = False
svg_lib_usage = True

app = Flask(__name__)

def load_database():
	global cursor, conn
	conn = psycopg2.connect(dbname=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST)
	cursor = conn.cursor()

def load_favicon(): # Loading favicon image
	img = Image.open('favicon.png')
	img_byte_arr = io.BytesIO()
	img.save(img_byte_arr, format='PNG')
	favicon_loaded = img_byte_arr.getvalue()

def parse_parameters(parameters, etag=None):
	global cursor, conn, database_usage, svg_lib_usage
	#if 'avicon.ico' in parameters: # Check if web asking for favicon
	#	return b'' #self.favicon

	parameters = dict(parameters)

	if database_usage and not cursor:
		load_database()

	parameters['database'] = cursor
	parameters['etag'] = etag
	parameters['svg'] = svg_lib_usage

	return renderer.make_photo(**parameters)

def make_error_response(error, status=400):
	resp = Response(error, status=status)
	resp.headers['Content-type'] = "text/html"

	return resp

def make_response(request):
	global svg_lib_usage
	if 'ETag' in request.headers:
			out = parse_parameters(request.args, request.headers['ETag'])
	else:
		out = parse_parameters(request.args)

	if out.__class__.__name__ == 'int':
		resp = Response(status=out)
	elif out.__class__.__name__ == 'tuple' and out[0].__class__.__name__ == 'int':
		resp = Response(f'<title>{out[0]}</title>\n<body>\n<p>{out[1]}</p>\n</body>', status=out[0])
		resp.headers['Content-type'] = "text/html"
	else:
		image = out[0]
		etag = out[1]
		resp = Response(image, status=200)
		resp.headers['Content-type'] = 'image/png'
		resp.headers['ETag'] = etag

	return resp

@app.route('/uc/v2/avatar', methods=['GET'])
def do_GET(): # TODO HTTP ETAG
	global cursor, conn, database_usage, debug_mode, svg_lib_usage
	if database_usage and not conn:
		load_database()

	if debug_mode:
		return make_response(request)

	try:
		return make_response(request)
	except Exception as e:
		return make_error_response('<title>Wrong arguments</title>\n<body>\n<p>Something got wrong, check arguments</p>\n<p>{}</p>\n</body>'.format(e))

def run(db_usage = True, debug=False, svg=True):
	global database_usage, debug_mode, svg_lib_usage
	database_usage = db_usage
	debug_mode = debug
	svg_lib_usage = svg
	thread = threading.Thread(target=caching.check_expiration_thread)
	thread.start()

	try:
		app.run(host=SERVICE_HOST, port=SERVICE_PORT, debug=debug)
	except KeyboardInterrupt:
		cursor.close()
		conn.close()


#run(handler_class=HttpGetHandler)
