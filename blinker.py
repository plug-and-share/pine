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
import subprocess

import branch

class Blinker:
	EOF = b'\n\r\t'

	def __init__(self, options, args):
		self.options = options
		self.args = args

	def run(self):
		try:
			lbranch = branch.Branch(65499)
		except ConnectionRefusedError:
			subprocess.Popen(['python3', 'log.py'])
			print('Feedback: pine is running. To confirm use pine --config to check the state.')
			return
		lbranch.send(b'\x00' + Blinker.EOF)
		resp = lbranch.recv()
		code, payload = resp[:1], resp[1:-3]
		if code == b'\x00':
			if payload == b'running':
				print('Feedback: pine is already running. No action was taken.')
			elif payload == b'paused':
				# action = ''
				# while action not in ('Y', 'y', 'n', 'N'):
					# action = input('Warning: pine was paused. You want to rerun it? [Y/n] ')
				# if action == 'Y' or action == 'y':
					# print('blinker.py:DEV: self.rerun()')
				print('Feedback: pine is running again.')
			else:
				print('Error: Communication failed. Please try again later.')
		else: 
			print('Error: Something uncommon happened. Please try again later.')

	def pause(self):
		try:
			lbranch = branch.Branch(65499)
		except ConnectionRefusedError:
			print('Feedback: Was not possible to pause pine. Pine is not running. ')
			return 
		lbranch.send(b'\x01' + Blinker.EOF)
		resp = lbranch.recv()
		code, payload = resp[:1], resp[1:-3]
		if code == b'\x01':
			if payload == b'pause':
				print('Feedback: pine was paused. To confirm use pine --config to check the state.')
			elif payload == b'paused':
				print('Feedback: pine is already paused. No action was taken')
			else:
				print('Error: Communication failed. Please try again later.')
		else:
			print('Error: Something uncommon happaned. Please try again later.')

	def stop(self): 
		try:
			lbranch = branch.Branch(65499)
		except ConnectionRefusedError:
			print('Feedback: pine is not running or paused. No action was taken.')
			return
		lbranch.send(b'\x02' + Blinker.EOF)

	def collaborate(self, payload):
		print('Debug collaborate')
		try:
			lbranch = branch.Branch(65499)
		except ConnectionRefusedError:
			print('Feedback: pine is not running. No action was taken.') #TODO: Por enquanto nao eh possivel colaborar se o pine nao estiver rodando 
			return
		print(b'\x03' + payload.encode() + Blinker.EOF)
		lbranch.send(b'\x03' + payload.encode() + Blinker.EOF)
		#resp = lbranch.recv() 


	def descollaborate(self):
		try:
			lbranch = branch.Branch(65499)
		except ConnectionRefusedError:
			print('Feedback: You don\'t make part of none collaboration. No action was taken.') #TODO: Por enquanto nao eh possivel descolaborar se o pine nao estiver rodando 
			return
		lbranch.send(b'\x04' + Blinker.EOF)

	def resource(self, param):
		pass

	def config(self): # fazer metodo para obter os dados
		print('\npine configuration:')
		print('	state        ', '{running, paused, stopped}')
		print('	vm_vcpu      ', '1..*')
		print('	vm_cpu_set   ', 'i.e. x86')
		print('	vm_cpu_usage ', '0-100%')
		print('	vm_ram_usage ', '0..host_ram')
		if True: # esta realizando uma exploracao TODO
			print('	progress     ', 'X/100%')
		print()

	def blink(self):
		if self.options.run:
			self.run()
		elif self.options.pause:
			self.pause()
		elif self.options.stop:
			self.stop()
		elif self.options.collaborate:
			print(self.options.collaborate)
			self.collaborate(self.options.collaborate)
		elif self.options.descollaborate:
			self.descollaborate()
		elif self.options.resource:
			self.resource(self.options.resource) # idem
		elif self.options.config:
			self.config()
		else:
			print('Cupid\nVersion 0.0.0\nBy The Cupid Team: https://github.com/plug-and-share/pine\nUsing python >=3')