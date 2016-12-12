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
import branch

class Blinker:
	'''
	[code|feedback_type|EOF]

	feedback_types:
		-ok|received
		-bad|received but an error occurs
		-not sure|send again
	'''
	def __init__(self, options, args):
		self.options = options
		self.args = args
		self.branch = Branch(65499)

	def run(self):
		self.branch.send(b'00' + b'\n\r\t') # code + EOF
		feedback = self.branch.recv()
		code, feedbackt = feedback[:2], feedback[2:-3]
		if code != b'00':
			pass # TODO o que fazer se isso acontencer
		if feedbackt == 	

	def pause(self):
		pass

	def stop(self):
		pass

	def collaborate(self, id):
		pass

	def resource(self, param):
		pass

	def config(self):
		'''
		STATE     running, paused, stopped
		VCPU      N_DE_CPUS
		CPU_SET   e.g. x86
		CPU_USAGE 0-100%
		REAL TIME
			CPU USAGE
			RAM USAGE
		IF COLLABORATING SHOW
			EXPLORATION PROGRESS X/Y
		'''
		pass

	def blink(self):
		if self.options.run:
			self.run()
		elif self.options.pause:
			self.pause()
		elif self.options.stop:
			self.stop()
		elif self.options.collaborate:
			self.collaborate(self.options.collaborate) # verificar se eh assim
		elif self.options.resource:
			self.resource(self.options.resource) # idem
		elif self.options.config:
			self.config()
