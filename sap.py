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
'''
import getpass
import sys
import subprocess
import shlex
import time

import pexpect

from common import Common

class Sap:

	vm_identifier = 'PineVM'

	def start(self):
		Common.msg_to_user('cloning virtual machine image', Common.INFO_MSG)
		cmd = shlex.split('virt-clone --connect=qemu:///system -o CupidVM -n ' + self.vm_identifier + ' -f /var/lib/libvirt/images/' + self.vm_identifier + '.img')
		p = subprocess.Popen(cmd).wait()
		if p == 0:
			Common.msg_to_user('virtual machine image copy created', Common.INFO_MSG)
		else:
			Common.msg_to_user('was not possible clone virtual machine image. HELP MSG', Common.ERRO_MSG)
			return False		
		Common.msg_to_user('booting virtual machine', Common.INFO_MSG)
		cmd = shlex.split('virsh start ' + self.vm_identifier)
		p = subprocess.Popen(cmd).wait()
		if p == 0:
			Common.msg_to_user('virtual machine started', Common.INFO_MSG)
		else:
			Common.msg_to_user('was not possible start virtual machine', Common.ERRO_MSG)
			return False
		Common.msg_to_user('authenticating ssh with virtual machine', Common.INFO_MSG)
		time.sleep(60)
		ssh_cmd = './sap_util.sh ' + self.vm_identifier
		child = pexpect.spawn(ssh_cmd, timeout=None)
		child.expect(['password: '])
		child.sendline('Omap2014')
		child.expect(pexpect.EOF)
		child.close()
		if child.exitstatus == 0:
			Common.msg_to_user('ssh authentication done', Common.INFO_MSG)
		else:
			Common.msg_to_user('was not possible authenticate ssh', Common.ERRO_MSG)
			return False
		return True

	def stop(self):		
		cmd = shlex.split('virsh destroy ' + self.vm_identifier)
		p = subprocess.Popen(cmd).wait()
		if p == 0:
			Common.msg_to_user('virtual machine was turned off', Common.INFO_MSG)
		cmd = shlex.split('virsh undefine ' + self.vm_identifier)
		p = subprocess.Popen(cmd).wait()
		if p == 0:
			Common.msg_to_user('virtual machine image was undefined', Common.INFO_MSG)
		else:
			Common.msg_to_user('was not possible undefine virtual machine image', Commoin.ERRO_MSG)
			return False
		cmd = shlex.split('sudo rm /var/lib/libvirt/images/' + self.vm_identifier + '.img')		
		p = subprocess.Popen(cmd).wait()
		if p == 0:
			Common.msg_to_user('virtual disk was erased', Common.INFO_MSG)
		else:
			Common.msg_to_user('was not possible erase virtual disk', Common.ERRO_MSG)
			return False
		return True
		
	def pause(self):
		cmd = shlex.split('virsh shutdown ' + self.vm_identifier)
		p = subprocess.Popen(cmd).wait()
		if p == 0:
			Common.msg_to_user('virtual machine was turned off', Common.INFO_MSG)
		else:
			Common.msg_to_user('was not possible pause virtual machine', Common.ERRO_MSG)
			return False
		return True

	def resume(self):
		cmd = shlex.split('virsh start ' + self.vm_identifier)
		p = subprocess.Popen(cmd).wait()
		if p == 0:
			Common.msg_to_user('virtual machine was resumed', Common.INFO_MSG)
		else:
			Common.msg_to_user('was not possible resume virtual machine', Common.ERRO_MSG)
			return False
		return True
 
	def communicate(self, instruction):
		print( "comunicate")
		vm_ip = subprocess.check_output('arp -an | grep \"`virsh dumpxml PineVM | grep \"mac address\" | sed \"s/.*\'\\(.*\\)\'.*/\\1/g\"`\" | awk \'{gsub(/[\\(\\)]/,\"\",$2); print $2}\'', shell=True)[:-1].decode()
		host_ip = subprocess.check_output('/sbin/ifconfig eth0 | grep \'inet addr\' | cut -d: -f2 | awk \'{print $1}\'', shell=True)[:-1].decode()
		Common.msg_to_user(instruction, Common.DBUG_MSG)
		subprocess.Popen('ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null cupid@' + vm_ip + ' \'python3 script.py ' + host_ip + ' ' + instruction.decode() + '\'', shell=True)