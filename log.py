'''
Copyright (c) 2016-2017 Plug-and-share
All rights reserved.
The license below extends only to copyright in the software and shall
not be construed as granting a license to any other intellectual
property including but not limited to intellectual property relating
to a hardware implementation of the functionality of the software
licensed hereunder.  You may use the software subject to the license
terms below provided that you ensure that this notice is replicated
unmodified and in its entirety in all distributions of the software,
modified or unmodified, in source code or in binary form.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met: redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer;
redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution;
neither the name of the copyright holders nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

VERSION        v0.0.0
DATE           12/08/2016
AUTHORS        TASHIRO
PYTHON_VERSION v3
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
	EOF = b'\n\r\t'
	
	def __init__(self):
		self.sock = socket.socket()
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
						req[fileno] += conns[fileno].recv(1024)
						if Log.EOF in req[fileno]:						
							resp[fileno] = self.action(req[fileno][:-3])
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

	def run(self):
		return b'00' + b'running' + Log.EOF

	def pause(self):
		# Antes precisa de um metodo para pausar a vm TODO
		# Mandar uma mensagem para o UI avisando que foi pausado TODO
		msg = b''		
		while 1:
			while EOL not in msg:
				msg += self.sock.recv(1024)
			code = msg[:2]
			if code == b'00': # user ask to rerunning
				return b'rerunning'
			elif code == b'02': # user ask to stop
				self.stop() # Precisa comunicar com a vm e com o broker TODO

	def stop(self):
		pass

	def collaborate(self, id):
		pass

	def resource(self, param):
		pass

	def action(self, msg):
		code, payload = msg[:2], msg[2:-3] # the two frist 
		if code == b'00':
			return self.run()
		elif code == b'01':
			return self.pause()
		elif code == b'02':
			return self.stop()		
		elif code == b'03': 
			return self.collaborate(payload)
		elif code == b'04':
			return self.resource(payload)
		
if __name__ == '__main__':
	pine_log = Log()
	pine_log.run()
