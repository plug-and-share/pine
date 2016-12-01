'''
LICENCE_DESCRIPTION

VERSION: v0.001
DATE: 12/01/2016
AUTHORS: Canabarro, Dias, Tashiro
PYTHON_VERSION: v3
'''
import optparse
import socket

def is_running():
	'''
	Verify if exist a pine process running
	'''
	with socket.socket() as sck:
		try:
			sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sck.bind(('localhost', 50000))
			sck.connect(('localhost', 54321))
			sck.settimeout(1)
			data = sck.recv(1024)
			print(data)
		except:
			return False
	return True

def run():
	'''
	Start the pine process
	'''
	if not is_running():
		with socket.socket() as sck:
			sck.bind(('localhost', 54321))
			sck.listen(1)
			while True:
				conn, addr = sck.accept()
				print('sending...')
				conn.send(b'hello')								

def command():
	'''
	Show the available commands and parse them
	'''
	usage = 'TODO_LIKE_SNORT pine <command> <args>'
	parser = optparse.OptionParser(usage=usage)
	parser.add_option('-r', '--run', action='store_true', 
			help='Start running pine')
	parser.add_option('-p', '--pause', action='store_true', 
			help='Pause running pine')
	parser.add_option('-s', '--stop', action='store_true', 
			help='Shutdown pine')
	parser.add_option('-c', '--collaborate', type='string', 
			help='Allocate the machine resource to some application')
	parser.add_option('-R', '--resource', action='store_true', 
			help='Manage the resource usage of the machine')
	parser.add_option('-C', '--config', action='store_true',
			help='Show the actual pine configuration')
	return parser.parse_args()

if __name__ == '__main__':
	opt, args = command()
	if opt.run:
		print('run')
	elif opt.pause:
		print('pause')
	elif opt.stop:
		print('stop')
	elif opt.collaborate:
		print('collaborate')
	elif opt.resource:
		print('resource')
	elif opt.config:
		print('config')




