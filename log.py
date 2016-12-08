'''
LICENCE_DESCRIPTION

VERSION: -
DATE: 12/08/2016
AUTHORS: Tashiro
PYTHON_VERSION: 3
'''
import select
import socket
import queue

class Log:
	'''
	Funciona como o controle entre os serviços
	'''
	def __init__(self):
		self.sock = socket.socket()
		self.sock.bind(('localhost', 65500))
		self.sock.listen(5)
		
	def run(self):
		inputs = [self.sock]
		outputs = []
		msg_queues = {}		
		while 1:
			read, write, error = select.select(inputs, outputs, inputs)
			print('reading#debug')
			for r in read:
				if r is self.sock:
					conn, addr = r.accept()
					conn.setblocking(False)
					inputs.append(conn)
					msg_queues[conn] = queue.Queue()
				else:
					chunk = r.recv(1024)
					print('receive ', chunk)
					if chunk:
						msg_queues[r].put(chunk)
						if r not in outputs:
							outputs.append(r)
					else:
						if r in outputs:
							outputs.remove(r)
						inputs.remove(r)
						r.close()
						del msg_queues[r]
			print('writing#debug')
			for w in write:
				try:
					next_msg = msg_queues[w].get_nowait()
				except queue.Empty:
					outputs.remove(w)
				else:
					w.send(next_msg) # call back()
			print('errors#debug')
			for e in error:
				inputs.remove(e)
				if e in outputs:
					outputs.remove()
				e.close()
				del msg_queues[e]

	def callback(self, msg):
		print(msg)
		
	def recv(self, sock):
		msg = b''
		while 1:
			chunk = sock.recv(1024)
			if chunk == b'':
				break
			msg += chunk
		return msg
					
	def send(self, branch_port, msg):
		self.socket.send(msg)	
		
if __name__ == '__main__':
	pine_log = Log()
	pine_log.run()
