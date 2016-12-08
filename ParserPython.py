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
	
