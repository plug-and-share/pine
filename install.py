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
# Dependendcias 
#	libvirt: sudo apt-get install libvirt-bin
#	qemu   : sudo apt-get install qemu-utils qemu-kvm
import errno
import os
import shutil
import sys

def copy_files(src, dest):
	try:
		shutil.copytree(src, dest)
	except OSError as exc: 
		if exc.errno == errno.ENOTDIR:
			shutil.copy(src, dst)
		else:
			raise

if __name__ == '__main__':
	try:
		if '-u' in sys.argv:
			if os.path.exists('/usr/local/bin/pinesrc'):
				os.system('rm -rf /usr/local/bin/pinesrc')
				os.system('rm /usr/local/bin/pine')
			else:
				print('[info] pine is not installed')
		else:
			if not os.path.exists('/usr/local/bin/pinesrc'):
				print('[info] installing dependencies')
				if os.system('sudo apt-get install libvirt-bin qemu-utils qemu-kvm') != 0:
					print('[erro] was not possible to install the dependences (libvirt-bin or qemu-utils or qemu-kvm)')
					exit()	
				print('[info] copying source files to /usr/local/bin/')
				copy_files(os.getcwd(), '/usr/local/bin/pinesrc')
				print('[info] adding to pine execution privileges')
				os.system('install -o root -m 555 pine /usr/local/bin')		
				os.system('sudo chmod +x /usr/local/bin/pinesrc/sap_util.sh')
				print('[info] pine was installed')
			else:
				print('[info] pine is already installed')
	except PermissionError:
		print('[erro] try again using sudo privileges')