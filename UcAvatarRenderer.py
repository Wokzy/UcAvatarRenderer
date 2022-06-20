#import sys
import http_server
#import renderer
#from config import *

__author__ = 'Yegor Yershov'

'''
def see_help():
	string = \
	f'Usage: \n\t{sys.argv[0]} [OPTIONS]\n\n' + \
	' -u  --user       |  user id (required)\n' + \
	' -f  --file_name  |  output file name (default user id)\n'# + \
	#'\n'

	print(string)

args = sys.argv[1::]

if "--help" in args or "-h" in args:
	see_help()
	exit()

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

http_server.run(handler_class=http_server.HttpGetHandler)