import io
import caching
import renderer
import psycopg2
import threading

from config import *
from PIL import Image
from flask import Flask, jsonify, request, Response

__author__ = 'Yegor Yershov'

global cursor, conn, database_usage, debug_mode
favicon_loaded = False
cursor = False
conn = None
database_usage = True
debug_mode = False

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
	global cursor, conn, database_usage
	#if 'avicon.ico' in parameters: # Check if web asking for favicon
	#	return b'' #self.favicon

	parameters = dict(parameters)

	if database_usage and not cursor:
		load_database()

	parameters['database'] = cursor
	parameters['etag'] = etag

	return renderer.make_photo(**parameters)


@app.route('/uc/v2/avatar', methods=['GET'])
def do_GET(): # TODO HTTP ETAG
	global cursor, conn, database_usage, debug_mode
	if database_usage and not conn:
		load_database()


	if debug_mode:
		if 'ETag' in request.headers:
			out = parse_parameters(request.args, request.headers['ETag'])
		else:
			out = parse_parameters(request.args)

		if out.__class__.__name__ == 'int':
			resp = Response(status=304)
		else:
			image = out[0]
			etag = out[1]
			resp = Response(image, status=200)
			resp.headers['Content-type'] = 'image/png'
			resp.headers['ETag'] = etag

		return resp

	try:
		if 'ETag' in request.headers:
			out = parse_parameters(request.args, request.headers['ETag'])
		else:
			out = parse_parameters(request.args)

		if out.__class__.__name__ == 'int':
			resp = Response(status=304)
		else:
			image = out[0]
			etag = out[1]
			resp = Response(image, status=200)
			resp.headers['Content-type'] = 'image/png'
			resp.headers['ETag'] = etag

		return resp
	except Exception as e:
		resp = Response('<title>Wrong arguments</title>\n<body>\n<p>Something got wrong, check arguments</p>\n<p>{}</p>\n</body>'.format(e), status=400)
		resp.headers['Content-type'] = "text/html"
		return resp

def run(db_usage = True, debug=False):
	global database_usage, debug_mode
	database_usage = db_usage
	debug_mode = debug
	thread = threading.Thread(target=caching.check_expiration_thread)
	thread.start()

	try:
		app.run(host=SERVICE_HOST, port=SERVICE_PORT, debug=debug)
	except KeyboardInterrupt:
		cursor.close()
		conn.close()


#run(handler_class=HttpGetHandler)
