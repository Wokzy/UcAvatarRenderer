import io
import caching
import renderer
import psycopg2
import threading

from config import *
from PIL import Image
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

__author__ = 'Yegor Yershov'

class HttpGetHandler(BaseHTTPRequestHandler):
	favicon_loaded = False
	database_loaded = False

	def load_favicon(self): # Loading favicon image
		img = Image.open('favicon.png')
		img_byte_arr = io.BytesIO()
		img.save(img_byte_arr, format='PNG')
		self.favicon = img_byte_arr.getvalue()
		self.favicon_loaded = True

	def parse_parameters(self):
		parameters = self.path[2::].split('&')

		if 'avicon.ico' in parameters: # Check if web asking for favicon
			return self.favicon

		parameters_dict = {'database':self.cursor}

		for param in parameters:
			parameter = param.split('=')
			parameters_dict[parameter[0]] = parameter[1].replace('+', ' ')

		return renderer.make_photo(**parameters_dict)

	def load_database(self):
		self.conn = psycopg2.connect(dbname=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST)
		self.cursor = self.conn.cursor()
		self.database_loaded = True

	def do_GET(self):
		if not self.favicon_loaded:
			self.load_favicon()
		if not self.database_loaded:
			self.load_database()

		#try:
		image = self.parse_parameters()
		self.send_response(200)
		self.send_header("Content-type", "image/jpg")
		self.end_headers()
		self.wfile.write(image)
		#except Exception as e:
		#	self.send_response(404)
		#	self.send_header("Content-type", "text/html")
		#	self.end_headers()
		#	self.wfile.write('<title>Wrong arguments</title>'.encode())
		#	self.wfile.write('<body>'.encode())
		#	self.wfile.write('Something got wrong, check arguments'.encode())
		#	self.wfile.write(f'{e}</body>'.encode())

	do_DELETE = do_GET

def run(handler_class, server_class=HTTPServer):
	thread = threading.Thread(target=caching.check_expiration_thread)
	thread.start()

	server_address = ('', 8000)
	httpd = server_class(server_address, handler_class)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		handler_class.cursor.close()
		handler_class.conn.close()
		httpd.server_close()


#run(handler_class=HttpGetHandler)
