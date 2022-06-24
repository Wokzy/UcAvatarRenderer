import sys
import http_server
#import renderer
#from config import *

__author__ = 'Yegor Yershov'

def see_help():
	string = \
	f'Usage: \n\t{sys.argv[0]} [OPTIONS]\n\n' + \
	'-h, --help         | see this message\n' + \
	'    --no-database  | Do not connect to database (some parameters wont be avalible)\n' + \
	'    --debug        | Turn on debug mode, all occuring errors will be shown in console\n' + \
	'\n\tHTTP API OPTIONS:\n' + \
	' name*             | Generate avatar from name\n' + \
	' chat_id/user_id*  | Generate or get avatar for user/chat from its name or url\n' + \
	' background        | (HSV) By default it is being generated by hash from avatar string\n' + \
	' main_background   | (RGBA) By default is trasparent\n' + \
	' size              | (H / WxH) Size of avatar from 16 to 512, by default 64x64\n' + \
	' url               | Get avatar from url. Base64, svg formats are supported\n' + \
	' client            | web/android/ios (any)\n' + \
	' push              | (True/False) Add push image to avatar or not\n' + \
	' theme             | (dark/light) Change theme. Isnt working yet\n\n' + \
	'\t Usage Examples:\n' + \
	'http://<HOST>:<PORT>/uc/v2/avatar?name=Yegor+Yershov&size=256\n' + \
	'http://<HOST>:<PORT>/uc/v2/avatar?chat_id=12345&size=250x500&background=yellow&push=True&client=web\n' + \
	'http://<HOST>:<PORT>/uc/v2/avatar?name=Yegor%20Yershov&size=360&url=https://randomwordgenerator.com/img/picture-generator/record-336626_640.jpg'
	'http://<HOST>:<PORT>/uc/v2/avatar?name=Privet%20Vsem&size=512&main_background=120,240,125&theme=light'

	print(string)

args = sys.argv[1::]
database_usage = True
debug = False

if "--help" in args or "-h" in args:
	see_help()
	sys.exit()
elif "--no-database" in args:
	print('Running without database')
	database_usage = False
if "--debug" in args:
	print('Running debug mode')
	debug = True

'''
#arguments = {'-u':'user_id', '--user':'user_id', '-f':'file_name', '--file_name':'file_name'}
#conf = {}

for i in range(len(args)):
	if args[i][0] == '-':
		conf[arguments[args[i]]] = args[i+1]

if 'user_id' not in conf:
	raise RuntimeError('User id was not mentioned, please enter -u/--user {USERID}!')
else:
	conf['user_id'] = int(conf['user_id'])

if 'file_name' not in conf:
	conf['file_name'] = conf['user_id']

cursor.execute('SELECT * FROM users WHERE user_id = {}'.format(conf['user_id']))
user = cursor.fetchone()
user_avatar_url = user[6] # avatar_url column
user_nickname = user[2]

print(user)

cursor.close()
conn.close()
'''

http_server.run(database_usage, debug)