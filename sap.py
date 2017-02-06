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

class Sap:

	vm_identifier = "AutomaticCopy"

	def start(self):
		print('[Feedback] instantiating VM.')
		# Clone an existing VM image
		command_line = shlex.split("virt-clone --connect=qemu:///system -o CupidVM -n "+self.vm_identifier+" -f /var/lib/libvirt/images/"+self.vm_identifier+".img")
		p = subprocess.Popen(command_line).wait()
		if p == 0:
			print("[Feedback] VM copy created...")
		else:
			print("[Error] Process Failed")
			exit()		
		# Boot the created copy
		command_line = shlex.split("virsh start " + self.vm_identifier)
		p = subprocess.Popen(command_line).wait()
		if p == 0:
			print("[Feedback] VM started!")
		else:
			print("[Error] Process Failed")
			exit()		
		time.sleep(60)
		# SSH Authorized Key Authentication 
		ssh_cmd = './sap_util.sh ' + self.vm_identifier                                                                                                                 
		child = pexpect.spawn(ssh_cmd, timeout=None)                                                                                                                            
		child.expect(['password: '])                                                                                                                                                                                                                                                                                               
		child.sendline('Omap2014')                                                                                                                                                   
		child.expect(pexpect.EOF)                                                                                                                                                  
		child.close()                                                                                                                                                              		
		if child.exitstatus == 0:
			print("[Feedback] SSH Authentication done!")
		else:
			print("[Error] Failed")

	def stop(self):		
		passw = getpass.getpass()
		# Turn off the VM
		command_line = shlex.split("virsh destroy " + self.vm_identifier)
		p = subprocess.Popen(command_line).wait()
		if p == 0:
			print("[Feedback] VM Destroyed!")
		else:
			print("[Feedback] VM is not running, the 1st step isn't necessary...")
		# Undefine VM
		command_line = shlex.split("virsh undefine " + self.vm_identifier)
		p = subprocess.Popen(command_line).wait()
		if p == 0:
			print("[Feedback] VM Undefined!")
		else:
			print("[Error] Process Failed")
			exit()			
		# Erase the Virtual Disk

		'''
		command_line = shlex.split("sudo rm /var/lib/libvirt/images/" + self.vm_identifier + ".img")
		
		p = subprocess.Popen(command_line).wait()
		if p == 0:
			print("[Feedback] Virtual Disk Erased!")
		else:
			print("[Error] Process Failed")
			exit()
		'''

		command_line = 'sudo rm /var/lib/libvirt/images/' + self.vm_identifier + '.img'                                                                                                                 
		child = pexpect.spawn(command_line, timeout=None)                                                                                                                            
		child.expect(['password: '])                                                                                                                                                                                                                                                                                               
		child.sendline(passw)                                                                                                                                                   
		child.expect(pexpect.EOF)                                                                                                                                                  
		child.close()                                                                                                                                                              		
		if child.exitstatus == 0:
			print("[Feedback] Virtual Disk Erased!")
		else:
			print("[Error] Process Failed")

		print("[Feedback] The VM is not running anymore")

	def pause(self):
		# pine-stop steps
		command_line = shlex.split("virsh shutdown " + self.vm_identifier)
		p = subprocess.Popen( command_line ).wait()
		if p == 0:
			print("VM turned off!")
		else:
			print("Process Failed")
			exit()

	def resume(self):
		# pine-stop steps
		command_line = shlex.split("virsh start " + self.vm_identifier)
		p = subprocess.Popen(command_line).wait()
		if p == 0:
			print("VM turned off!")
		else:
			print("Process Failed")
			exit()		

def main(args):					
	if sys.argv[1] == '5' :
		# Instructions
		command_line = shlex.split( sys.argv[2] )
		print( command_line )
		p = subprocess.Popen( command_line )
		
	if sys.argv[1] == b'\x06' :
		# Result steps
		#command_line = shlex.split( "ls -lah" )
		print( command_line )
		p = subprocess.Popen( command_line ).wait()
		if p == 0:
			print( "Procces Done!" )
		else:
			print( "Process Failed" )
			exit()
		
	if sys.argv[1] == b'\x04' :
		# pine-start steps
		#command_line = shlex.split( "ls -lah" )
		print( command_line )
		p = subprocess.Popen( command_line )
		
	return 0
		
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
