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
DATE           12/12/2016
AUTHORS        CANABARRO,DIAS,TASHIRO
PYTHON_VERSION v3
'''
import json
import subprocess

from branch import Branch
from common import Common


class Blinker:

	EOF = b'\n\r\t'
	port = 65499

	def __init__(self, options, args):
		self.options = options
		self.args = args

	def run(self): # OK*
		'''
		1° passo: verificar se o pine esta colaborando com alguem

		2° passo: Verifica o estado atual do pine.

		3° passo: Dependendo do seu estado uma ação é executada. Caso esteja rodando 
				  apenas avisa o usuário. Se estiver parado avisa o usuário e solici-
				  ta uma confirmação para voltar a rodar e avisa o *sleigh*. Se esti-
				  ver parado inicia o começa a rodar o pine.
		'''		
		process = Common.get_config_info(['process'])
		if not process:
			print('[Feedback] pine need to collaborating with an application to run.')
			return
		state = Common.get_config_info(['state'])
		if state == 'running':
			print('[Feedback] pine is already running. You can check the state using the --config command.')
		elif state == 'paused':
				confirm = ''
				while confirm not in ('Y', 'y', 'n', 'N'):
					confirm = input('[Warning] pine was paused. You want to rerun it? [Y/n] ')
				if confirm == 'Y' or confirm == 'y':
					branch = Branch(self.port, ('localhost', 65500))	
					branch.send(b'\x00' + Blinker.EOF)
					resp = branch.recv()
					branch.close()
					if resp[:-3] == b'running':
						Common.update_config({'state': 'running'})
						print('[Feedback] pine is rerunning again. You can check the state using the --config command')
		elif state == 'stopped':
			subprocess.Popen(['python3', 'log.py'])
			Common.update_config({'state': 'running'})			
			print('Feedback: pine is running. You can check the state using the --config command.')
			return

	def pause(self): # OK
		'''
		1° passo: Verifica o estado atual do pine.

		2° passo: Dependendo do seu estado uma ação é executada. Se estiver rodando ele
				  solicita uma confirmação da ação e avisa sobre as consequências dela. 
				  Caso esteja pausado ou parado, apenas avisa o usuário do seu estado.
		'''
		state = Common.get_config_info(['state'])
		if state == 'running':
			confirm = ''
			while confirm not in ('Y', 'y', 'n', 'N'):
				confirm = input('[Warning] pine is running. All process will be paused if you confirm the action [Y/n] ')
			if confirm == 'Y' or confirm == 'y':
				branch = Branch(self.port, ('localhost', 65500))
				branch.send(b'\x01' + Blinker.EOF)
				resp = branch.recv()
				branch.close()				
				if resp == b'paused' + Blinker.EOF:
					Common.update_config({'state': 'paused'})
					max_wait_time = Common.get_config_info(['process', 'max_wait_time'])					
					print('[Feedback] pine was paused. You can check the state using the --config command.')
					print('[Warning] You have', max_wait_time / 60, ' minutes before the actual processed data be discarded.')
					if max_wait_time:
						print('[Warning] You have', max_wait_time / 60, 'minutes before the actual processed data be discarded.')
		elif state == 'paused':
			print('[Feedback] pine is already paused. You can check the state using --config command.')	
		elif state == 'stopped':
			print('[Feedback] pine is stopped. No action was performed. You can check the state using --config command.')		

	def stop(self): # OK
		'''
		1° passo: Verifica o estado atual do pine.

		2° passo: Dependendo do seu estado uma ação é  executada. Se estiver  rodando ou
				  pausado pede para confirmar a ação e avisa sobre as consequências dela.
				  Se estiver parado, apenas avisa o usuário do seu estado.
		'''
		state = Common.get_config_info(['state'])
		if state == 'running' or state == 'paused':
			confirm = ''
			while confirm not in ('Y', 'y', 'n', 'N'):
				confirm = input('[Warning] pine is running or paused. All data will be descarted if you confirm the action [Y/n]')
			if confirm == 'Y' or confirm == 'y':
				try:
					branch = Branch(self.port, ('localhost', 65500))
					branch.send(b'\x02' + Blinker.EOF)
					resp = branch.recv()
					branch.close()
					if resp == b'stopped' + Blinker.EOF:
						Common.update_config({'state': 'stopped'})
						print('[Feedback] pine was stopped. You can check the state using --config command.')
				except ConnectionRefusedError:
					Common.update_config({'state': 'stopped'})
					print('[Feedback] pine was stopped. You can check the state using --config command.')
		elif state == 'stopped':
			print('[Feedback] pine is already stopped. None action was performed. You can check the state using --config command')		

	def collaborate(self, address): # OK
		'''
		1° passo: Checa se o pine já está colaborando. Se sim avisa o usuário e pede se ele deseja
			      parar de colaborar com a aplicação a tual.

		2° passo: Estabelece envia uma mensagem para o sleigh pedindo para colaborar com aquela
				  aplicação.

		3° passo: Atualiza as configurações do pine.
		'''
		process = Common.get_config_info(['process'])		
		if process:
			confirm = ''
			while confirm not in ('Y', 'y', 'n', 'N'):
				confirm = input('[Warning] pine is already collaborating with an application. You wish descollaborate with it and collaborate with another application [Y/n]')
			if confirm == 'Y' or confirm == 'y':
				self.descollaborate()
				Common.update_config({'process': None})
		try:
			branch = Branch(self.port, address)
		except ConnectionRefusedError:
			print('[Error] The address is invalid or the sleigh doesn\'t exist. Please try again.')
			return
		branch.send(b'\x03' + Blinker.EOF)
		resp = branch.recv()		
		branch.close()		
		payload = resp[:-3]
		method_name, vm_img, processing_time_limit, max_wait_time = payload.split()
		Common.update_config({
			'process': {
				'method_used': method_name.decode(), 
				'vm_img': vm_img.decode(),
				'sleigh_address': address,
				'processing_time_limit': int(processing_time_limit),
				'max_wait_time': int(max_wait_time)
			}
		})
		print('[Feedback] ...')

	def descollaborate(self): # OK*
		'''
		1° passo: Verifica se o pine esta colaborando com alguem

		2° passo: Avisa para o sleigh e o *pine* que está descolaborando com ele.

		3° passo: Atualiza as configurações do pine.
		'''
		process = Common.get_config_info(['process'])
		if process:
			try:
				with open('config.json') as config_file:
					config = json.load(config_file)
					branch = Branch(self.port, tuple(config['process']['sleigh_address']))
			except ConnectionRefusedError:
				print('[Error] Was not possible to communicate with sleigh. Please check if it is still running.')
				return 
			branch.send(b'\x04' + Blinker.EOF)
			resp = branch.recv()
			branch.close()
			code, payload = resp[:1], resp[1:-3]
			print('[Feedback] ....')
			Common.update_config({'process': None})
		else:
			print('[Feedback] pine was not collaborating with an aplication. No action was performed.')			

	def resource(self, param):
		pass

	def config(self): 
		print('--------------------------------')
		print('config:')
		print('	state:       ', Common.get_config_info(['state']))
		print('	vm_vcpu:     ', Common.get_config_info(['vm', 'vcpu']))
		print('	vm_cpu_set:  ', Common.get_config_info(['vm', 'cpu_set']))
		print('	vm_cpu_usage:', Common.get_config_info(['vm', 'cpu_usage']))
		print('	vm_ram_usage:', Common.get_config_info(['vm', 'ram_usage']))
		#if config['process']:
		#	print('	progress     ', config['process']['progress'])
		print('--------------------------------')

	def blink(self):
		if self.options.run:
			self.run()
		elif self.options.pause:
			self.pause()
		elif self.options.stop:
			self.stop()
		elif self.options.collaborate:
			ip, port = self.options.collaborate.split()
			self.collaborate((ip, int(port)))
		elif self.options.descollaborate:
			self.descollaborate()
		elif self.options.resource:
			self.resource(self.options.resource) # idem
		elif self.options.config:
			self.config()
		else:
			print('Cupid\nVersion 0.0.0\nBy The Cupid Team: https://github.com/plug-and-share/pine\nUsing python >=3')