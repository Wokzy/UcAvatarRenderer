import io
import caching
import renderer
import psycopg2
import threading

from config import *
from PIL import Image
from flask import Flask, jsonify, request, Response

__author__ = 'Yegor Yershov'

favicon_loaded = False
cursor = False
conn = None

app = Flask(__name__)

def load_database():
	conn = psycopg2.connect(dbname=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST)
	cursor = conn.cursor()

def load_favicon(): # Loading favicon image
	img = Image.open('favicon.png')
	img_byte_arr = io.BytesIO()
	img.save(img_byte_arr, format='PNG')
	favicon_loaded = img_byte_arr.getvalue()

def parse_parameters(parameters):
	#if 'avicon.ico' in parameters: # Check if web asking for favicon
	#	return b'' #self.favicon

	parameters = dict(parameters)

	if not cursor:
		load_database()
	parameters['database'] = cursor

	return renderer.make_photo(**parameters)


@app.route('/uc/v2/avatar', methods=['GET'])
def do_GET():
	if not conn:
		load_database()

	try:
		image = parse_parameters(request.args)
		resp = Response(image, status=200)
		resp.headers['Content-type'] = 'image/png'
		return resp
	except Exception as e:
		resp = Response('<title>Wrong arguments</title>\n<body>\n<p>Something got wrong, check arguments</p>\n<p>{}</p>\n</body>'.format(e), status=400)
		resp.headers['Content-type'] = "text/html"
		return resp

def run():
	thread = threading.Thread(target=caching.check_expiration_thread)
	thread.start()

	try:
		app.run(host=SERVICE_HOST, port=SERVICE_PORT)
	except KeyboardInterrupt:
		cursor.close()
		conn.close()


#run(handler_class=HttpGetHandler)
