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
import os # Log.stop() temporary solution
import signal # Log.stop() temporary solution

class Log:
	'''
	Gerencia o fluxo de I/O entre tres componentes: broker, vm-manager e
	UI.  A comunicacao eh  feita via  TCP e sua porta padrao eh a 65500. 
	As  mensagens  enviadas  para  o  Log  possuem o  seguinte  formato:  
	[code|payload|EOF],  em que o code identifica  o tipo de  mensagem e 
	possue  um  byte,  o  payload  representa o conteudo da  mensagem  e 
	pode possuir um tamanho arbitrario e o EOF indica o fim da mensagem.		
	'''
	EOF = b'\n\r\t'
	
	def __init__(self):
		self.sock = socket.socket()
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('localhost', 65500))
		self.sock.listen(5)
		self.epoll = select.epoll()
		self.epoll.register(self.sock.fileno(), select.EPOLLIN)
		self.conns = {}
		self.req = {}
		self.resp = {}
		
	def run(self):
		try:
			while 1:
				events = self.epoll.poll(1)
				for fileno, event in events:
					if fileno == self.sock.fileno():
						conn, addr = self.sock.accept()
						conn.setblocking(0)
						self.epoll.register(conn.fileno(), select.EPOLLIN)
						self.conns[conn.fileno()] = conn
						self.req[conn.fileno()] = b''
					elif event & select.EPOLLIN:
						self.req[fileno] += self.conns[fileno].recv(1024)
						if Log.EOF in self.req[fileno]:						
							self.resp[fileno] = self.action(self.req[fileno][:-3], self.conns[fileno])
							#if self.resp[fileno] != b'':
							if self.resp[fileno] != None:
								self.epoll.modify(fileno, select.EPOLLOUT)
					elif event & select.EPOLLOUT:
						bw = self.conns[fileno].send(self.resp[fileno])
						self.resp[fileno] = self.resp[fileno][bw:]
						if len(self.resp[fileno]) == 0:
							self.epoll.modify(fileno, 0)
							self.conns[fileno].shutdown(socket.SHUT_RDWR)
					elif event & select.EPOLLHUP:
						self.epoll.unregister(fileno)
						self.conns[fileno].close()
						del self.conns[fileno]
		finally:
			self.epoll.unregister(self.sock.fileno())
			self.epoll.close()
			self.sock.close()

	def pause(self, conn):
		# self.pause_vm()
		conn.sendall(b'\x01' + b'pause' + Log.EOF)
		conn.close()
		while 1:
			conn, addr = self.sock.accept()
			msg = b''
			while Log.EOF not in msg:
				msg += conn.recv(1024)
			code = msg[:1]
			if code == b'\x00':
				conn.sendall(b'\x00' +  b'paused' + Log.EOF)
				conn.close()
				return b''
			elif code == b'\x01':
				conn.sendall(b'\x01' + b'paused' + Log.EOF)
				conn.close()
			elif code == b'\x02':
				self.stop()

	def stop(self): # temporary solution TODO (ver as consequencias dessa solucao)
		print('Feedback: pine was stopped')
		pid = os.getpid()
		os.kill(pid, signal.SIGTERM)	

	def collaborate(self, address, no): # TODO: Testar
		print('debug collaborate') # Execucao infinita
		def descollaborate(self):
		sock = socket.socket()
		sock = setblocking(0)
		sock.connect()
		self.resp[sock.fileno()] = b'\x04' + Log.EOF 

	def thanks(self): #send_result
		pass

	def leader(self): #instructions		
		pass

	def resource(self, param):
		pass

	def action(self, msg, conn):
		'''
		Dependendo do tipo de mensagem recebida uma diferente acao e tomada.
		Atualmente,  este metodo  impossibilita  qualquer  tipo de comunicao 
		enquanto estiver ativo, pois ele bloqueia o processo. 
		'''
		print('a', msg)
		code, payload = msg[:1], msg[1:]

		if code == b'\x00':
			return b'\x00' + b'running' + Log.EOF
		elif code == b'\x01':
			return self.pause(conn)
		elif code == b'\x02':
			return self.stop()		
		elif code == b'\x03': 
			print(payload)
			address, no = payload.split()
			return self.collaborate(address, no)
		elif code == b'\x04':
			return self.descollaborate()
		elif code == b'\x05':
			return self.resource(payload)
		
if __name__ == '__main__':
	pine_log = Log()
	pine_log.run()

"""
	1 byte | payload | EOF
	
	pine -> santa

		collaborate: \x04 | id | EOF (O servidor verifica se o id eh valido, caso sim incluia na lista de colaboradores 
		                              do processo. Caso o pine esteja rodando o broker comeca a enviar as instrucoes).
		descollaborate: \x05 | null | EOF (Caso o processo exista e esteja collaborando, exclui da lista).
		
		resultado: \x06 | resultado | EOF (A partir do address do colaborador o santa ja sabe com quem ele esta colaborando).

		pine-stop: \x07 | parou/pausou | EOF (Dependendo da configuracao do broker, caso ele pause ele pode manter  
		                                     descartar o que estava sendo processado e reenviar a instrucao ou esperar 
		                                     por um tempo limite o pine que parou terminar de processar).
		pine-start: \x08 | null | EOF

		instruction: \x09 | null | EOF (solicita uma instrucao)

	sleigh -> pine

		send-instruction: \x42 | payload | EOF

		ping: \x43 | null | EOF (verifica o estado do pine)

	config-broker:
		wait: true(tempo limite)/false
		wait2: tempo maximo para o pine processar uma instrucao


256

pine 0-41
sleigh 42-83
santa 84-125
north-pole 126-167
south-pole 168-209
cupid 209-255
		

	no is the new id  
"""