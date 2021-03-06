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
import getpass
import os 
import select
import signal
import socket
import sys

from common import Common
import sap

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
		self.sock.bind(('', 65500))
		self.sock.listen(5)
		self.epoll = select.epoll()
		self.epoll.register(self.sock.fileno(), select.EPOLLIN)
		self.conns = {}
		self.req = {}
		self.resp = {}
		self.c_address = tuple(Common.get_config_info(['process', 'sleigh_address']))
		self.vm_controller = sap.Sap()
		self.processing = False
		signal.signal(signal.SIGTERM, self.sigterm)
		
	def sigterm(self, signum, frame):
		'''
		Muda o estado caso o processo seja terminado inesperadamente. 
		TODO: Ver o que exatamente isso ira tratar
		'''
		Common.update_config({'state': 'stopped'})
		self.vm_controller.stop()
		sys.exit()

	def ping(self, address, msg):
		'''
		Estabelece uma conexão com sleigh e insere a mensagem na epoll para ser 
		enviada posteriormente.
		'''
		try:
			conn = socket.socket()
			conn.connect(address)
			conn.setblocking(0)
		except ConnectionRefusedError:
			return False
		self.epoll.register(conn.fileno(), select.EPOLLOUT)
		self.conns[conn.fileno()] = conn
		self.resp[conn.fileno()] = msg
		return True

	def pingoutin(self, address, msg):
		'''
		Estabelece uma conexão com o sleigh, manda uma mensagem e depois espera
		uma resposta.
		'''
		conn = socket.socket()
		conn.connect(address)
		conn.sendall(msg)
		conn.setblocking(0)
		self.epoll.register(conn.fileno(), select.EPOLLIN)
		self.conns[conn.fileno()] = conn
		self.req[conn.fileno()] = b''

	def run(self):
		Common.msg_to_user('preparing to launch virtual machine', Common.INFO_MSG)
		if self.vm_controller.start():
			Common.msg_to_user('pine is running. You can check the state using --config command', Common.INFO_MSG)
			Common.update_config({'state': 'running'})
			try:
				process = None
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
								if self.resp[fileno] != None:
									self.epoll.modify(fileno, select.EPOLLOUT)
								else:
									self.epoll.unregister(fileno)
									self.conns[fileno].close()
									del self.conns[fileno]					
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
					if self.processing == False:
						self.letter()
			finally:
				self.epoll.unregister(self.sock.fileno())
				self.epoll.close()
				self.sock.close()
				Common.update_config({'state': 'stopped'})
		else:
			pass

	def pause(self, conn): 
		'''
		1° passo: O Log recebe um comando do usuário requisitando que ele pause
		          o processamento de uma instrução.

		*2° passo: Avisa o sleigh que o pine pausou.	
		'''
		Common.msg_to_user('pausing virtual machine', Common.INFO_MSG)
		self.vm_controller.pause()
		conn.sendall(b'paused' + Log.EOF)
		conn.close()
		Common.msg_to_user('pine was paused. You can resume it using the run command', Common.INFO_MSG)
		Common.update_config({'state': 'paused'})
		while 1:
			conn, addr = self.sock.accept()
			msg = b''
			while Log.EOF not in msg:
				msg += conn.recv(1024)
			code = msg[:1]
			if code == b'\x00':
				self.vm_controller.resume()
				Common.update_config({'state': 'running'})
				conn.sendall(b'running' + Log.EOF)
				conn.close()
				break
			elif code == b'\x01':
				conn.sendall(b'paused' + Log.EOF)
				conn.close()
			elif code == b'\x02':
				self.stop(conn)

	def stop(self, conn):
		'''
		*1° passo: Verifica se algo está sendo processado. Caso sim, avisa o sleigh
				  que o pine se encerrará. Enquanto isso avisa o usuário que está
				  esperando a resposta do sleigh.
		
		2° passo: Um comando para desligar a máquina virtual é chamado. Enquanto
				  isso avisa o usuário sobre isso.

		3° passo: Avisa o sleigh que o pine parou.
		'''
		Common.msg_to_user('warning sleigh that pine will stop', Common.INFO_MSG)
		self.ping(self.c_address, b'\x07' + Log.EOF)
		conn.sendall(b'stopped' + Log.EOF)
		Common.msg_to_user('killing pine process and stopping virtual machine', Common.INFO_MSG)
		os.kill(os.getpid(), signal.SIGTERM)

	def letter(self): #instructions
		'''
		1° passo: Manda uma mensagem para o sleigh solicitando uma nova instrução.
		
		2° passo: Registra a conexão com o sleigh na epoll para posteriormente rece-
				  be-la de forma que não bloqueia o programa.
		'''
		self.pingoutin(self.c_address, b'\x05' + Log.EOF)
		self.processing = True

	def thanks(self, result):
		'''
		Envia o resultado para o sleigh.
		'''
		self.ping(self.c_address, b'\x06' + result + Log.EOF)
		self.processing = False

	def process(self, payload):
		self.vm_controller.communicate(payload)

	def action(self, msg, conn):		
		code, payload = msg[:1], msg[1:]
		if code == b'\x00':
			return b'running' + Log.EOF
		elif code == b'\x01':
			return self.pause(conn)
		elif code == b'\x02':
			return self.stop(conn)
		elif code == b'\x43':
			return self.process(payload)
		elif code == b'\x99':
			return self.thanks(payload)

		
if __name__ == '__main__':
	pine_log = Log()
	pine_log.run()