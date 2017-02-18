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
import configparser
import subprocess

INI_Parser = configparser.ConfigParser()
INI_Parser._interpolation = configparser.ExtendedInterpolation()
INI_Parser.read("config.ini")
#~ print( Config.get( 'Virtual_Machine', 'NAME' ) )

p = subprocess.Popen( [ "virt install", "--name "+INI_Parser.get( 'Virtual_Machine', 'NAME' ),
	"--ram "+INI_Parser.get( 'Virtual_Machine', 'RAM' ),
	"--vcpu "+INI_Parser.get( 'Virtual_Machine', 'VCPU' ),
	"--cpuset "+INI_Parser.get( 'Virtual_Machine', 'CPUSET' ),
	"--cdrom "+INI_Parser.get( 'Virtual_Machine', 'CDROM' ),
	"--os-type "+INI_Parser.get( 'Virtual_Machine', 'OSTYPE' ),
	"--boot "+INI_Parser.get( 'Virtual_Machine', 'BOOT' ),
	"--disk "+INI_Parser.get( 'Virtual_Machine', 'DISK' ),
	"--graphics "+INI_Parser.get( 'Virtual_Machine', 'GRAPHICS' ),
	"--connect "+INI_Parser.get( 'Virtual_Machine', 'CONNECT' ),
	"--virt-type "+INI_Parser.get( 'Virtual_Machine', 'VIRTTYPE' ) ],
	shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
	
'''
def main(args):					
	if sys.argv[1] == '5' :
		# Instructions
		cmd = shlex.split( sys.argv[2] )
		print( cmd )
		p = subprocess.Popen( cmd )
		
	if sys.argv[1] == b'\x06' :
		# Result steps
		#cmd = shlex.split( 'ls -lah' )
		print( cmd )
		p = subprocess.Popen( cmd ).wait()
		if p == 0:
			print( 'Procces Done!' )
		else:
			print( 'Process Failed' )
			exit()
		
	if sys.argv[1] == b'\x04' :
		# pine-start steps
		#cmd = shlex.split( 'ls -lah' )
		print( cmd )
		p = subprocess.Popen( cmd )
		
	return 0
		
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
'''