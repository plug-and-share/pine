'''
LICENCE_DESCRIPTION

version=0.1
date=12/08/2016
authors=Tashiro
python=3
'''
import select
import socket

class Log:
	'''
	Gerencia o fluxo de I/O entre tres componentes: broker, vm-manager e
	UI.  A comunicacao eh  feita via  TCP e sua porta padrao eh a 65500. 
	As  mensagens  enviadas  para  o  Log  possuem o  seguinte  formato:  
	[code|payload|EOF],  em que o code identifica  o tipo de  mensagem e 
	possue  CODE_SIZE,  o  payload representa o conteudo da mensagem e o 
	EOF indica o fim da mensagem.		
	'''
	EOL1 = b'\n\n'
	EOL2 = b'\n\r\n'
	
	def __init__(self):
		self.sock = socket.socket()
		self.sock.bind(('localhost', 65500))
		self.sock.listen(5)
		self.epoll = select.epoll()
		self.epoll.register(self.sock.fileno(), select.EPOLLIN)
		
	def run(self):
		try:
			conns, req, resp = {}, {}, {}
			while 1:
				events = self.epoll.poll(1)
				for fileno, event in events:
					if fileno == self.sock.fileno():
						conn, addr = self.sock.accept()
						conn.setblocking(0)
						self.epoll.register(conn.fileno(), select.EPOLLIN)
						conns[conn.fileno()] = conn
						req[conn.fileno()] = b''
					elif event & select.EPOLLIN:
						# Nao vai funcionar se receber do broker
						# Alterar para suportar o proto-protocol
						req[fileno] += conns[fileno].recv(1024)
						if Log.EOL1 in req[fileno] and Log.EOL2 in req[fileno]:
							resp[fileno] = self.action(int(req[fileno][:-5]))
							self.epoll.modify(fileno, select.EPOLLOUT)
					elif event & select.EPOLLOUT:
						bw = conns[fileno].send(resp[fileno])
						resp[fileno] = resp[fileno][bw:]
						if len(resp[fileno]) == 0:
							self.epoll.modify(fileno, 0)
							conns[fileno].shutdown(socket.SHUT_RDWR)
					elif event & select.EPOLLHUP:
						self.epoll.unregister(fileno)
						conns[fileno].close()
						del conns[fileno]
		finally:
			self.epoll.unregister(self.sock.fileno())
			self.epoll.close()
			self.sock.close()

	def action(self, code):
		print('code:', code)
		if code == 0x0: # run code
			return b'run code received'
		elif code == 0x1: # pause code
			# self.pause()
			return b'pause code received'
		elif code == 0x2: # stop code
			# self.stop()
			return b'stop code received'
		elif code == 0x3: # collaborate code
			# self.collaborate()
			return b'collaborate code received'
		elif code == 0x4: # resource code
			# param = self.parseparam()
			# self.resource(param)
			return b'resource code received'
		elif code == 0x5: # config code
			# self.config()
			return b'config code received'
		
if __name__ == '__main__':
	pine_log = Log()
	pine_log.run()
