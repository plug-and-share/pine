'''
LICENCE_DESCRIPTION

VERSION: -
DATE: 12/08/2016
AUTHORS: Tashiro
PYTHON_VERSION: 3
'''
import socket

class Branch:
	'''
	Realiza a comunicação entre o Log e um serviço
	'''
	def __init__(self, service_port):
		self.sock = socket.socket()
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('localhost', service_port))
		self.sock.connect(('localhost', 65500)) # conecta ao Log usando sua porta padrão
		
	def send(self, msg):
		self.sock.sendall(msg)
		
	def recv(self):
		msg = b''
		while 1:
			chunk = self.sock.recv(1024)
			if chunk == b'':
				break
			msg += chunk
		return msg
		
if __name__ == '__main__':
	test_branch = Branch(60000)
	#~ print((b'Hello World' * 1000).__sizeof__())
	test_branch.send(b'Hello World')
