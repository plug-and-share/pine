'''
LICENCE_DESCRIPTION

VERSION: v0.001
DATE: 12/01/2016
AUTHORS: Canabarro, Dias, Tashiro
PYTHON_VERSION: v3
'''
import optparse							

def command():
	'''
	Show the available commands and parse them
	'''
	usage = 'Cupid\nVersion 0.0.0\nBy The Cupid Team: https://github.com/plug-and-share/\nUsing python >=3'
	parser = optparse.OptionParser(usage)
	parser.add_option('-r', '--run', action='store_true', 
			help='Start running pine')
	parser.add_option('-p', '--pause', action='store_true', 
			help='Pause running pine')
	parser.add_option('-s', '--stop', action='store_true', 
			help='Shutdown pine')
	parser.add_option('-c', '--collaborate', action='store_true', 
			help='Allocate the machine resource to some application')
	parser.add_option('-R', '--resource', action='store_true', 
			help='Manage the resource usage of the machine')
	parser.add_option('-C', '--config', action='store_true',
			help='Show the actual pine configuration')
	parser.add_option('-v', '--version', action='store_true',
			help='Cupid version number')
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
	elif opt.version:
		print('Cupid\nVersion 0.0.0\nBy The Cupid Team: https://github.com/plug-and-share/pine\nUsing python >=3')
