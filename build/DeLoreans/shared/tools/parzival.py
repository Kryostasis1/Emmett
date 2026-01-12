import argparse
import re
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("/root/Documents/data/emmett_config.ini")
enginfo = config_object['ENGINFO']

linedict = []
linenum = 0

#Header
print("""
__________                     .__              .__   
\\______   \\_____ ______________|__|__  _______  |  |  
 |     ___/\\__  \\\\_  __ \\___   /  \\  \\/ /\\__  \\ |  |  
 |    |     / __ \\|  | \\//    /|  |\\   /  / __ \\|  |__
 |____|    (____  /__|  /_____ \\__| \\_/  (____  /____/
                \\/            \\/              \\/ Emmett edition - v0.0.3          
                                                                                   
""")
usage_text = 'python parzival.py'
example_text = '''Example:
python parzival.py'''
parser = argparse.ArgumentParser(usage=usage_text, epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)

#Arguments
parser.add_argument("-f", "--file", help="Specify file to be parsed.\n", nargs='+', required=True)
parser.add_argument("-o", "--output", help="Specify output filename. \n", nargs="+")

args = parser.parse_args()

if not args.file:
	print("Nmap file must be specified using -f.")
	exit()
if len(args.file) > 1:
	print("Multiple input files detected. Parzival only allows 1 file per execution.")
	exit()
if args.output:
	if '.txt' in args.output[0]:
		outputFilename = str(args.output[0])
	else:
		outputFilename = str(args.output[0])+'.txt'

hostFilename = str(args.file[0])
with open(hostFilename, 'r') as f:
	firstline = f.readline()
	data = f.readlines()
if not 'Nmap' in firstline: #Check if inputted file is Nmap file.
	print('The submitted file does not appear to be an Nmap output file.')
	exit()
if '-sU' in firstline: #Check if UDP Scan
	if not args.output:
		outputFilename = './UDP_Output_Parsed.txt'
	newfile = open(outputFilename, 'a')
	for line in data: #Reading Lines
		linedict.append(line)
		if line in ['\n','\r\n'] or 'Nmap done at' in line: #Next Host Check
			linedictlength = len(linedict)
			if linedictlength == hostHeadersDictNum+2:
				del linedict[hostHeadersDictNum]
			for x in range(len(linedict)):
				newfile.write(linedict[x])
			linenum = 0
			linedict = []
			continue
		if 'Not shown:' in line and 'udp ports' in line:
			hostPortsDictNum = linenum
			hostPortsLine = line.split()
			hostPorts = int(hostPortsLine[2])
		if 'PORT' in line and 'STATE' in line and 'SERVICE' in line:
			hostHeadersDictNum = linenum
		if '53/udp' in line and 'open' in line and 'domain' in line:
			del linedict[linenum]
			hostPorts = hostPorts+1
			hostPorts = str(hostPorts)
			hostPortsLine[2] = hostPorts
			hostPortsLine.append('\n')
			FinalHostPortsLine = ' '.join(hostPortsLine)
			linedict[hostPortsDictNum] = FinalHostPortsLine
			continue
		if 'Increasing send delay for' in line: #Remove Delay Messages
			if not linedict:
				linedict = []
				continue
			else:
				del linedict[linenum]
				continue
		linenum = linenum+1						
	exit()
else: #TCP Scan
	if not args.output:
		outputFilename = './TCP_Output_Parsed.txt'
	tlsFilename = '/root/Documents/data/tls_hosts.txt'
	httpFileName = '/root/Documents/data/http_hosts.txt'
	newfile = open(outputFilename, 'w')
	tlsfile = open(tlsFilename, 'a')
	httpfile = open(httpFileName, 'a')
	for line in data:
		linedict.append(line)
		if line in ['\n','\r\n'] or 'Nmap done at' in line: #Next Host Check
			linedictlength = len(linedict)
			if linedictlength == hostHeadersDictNum+2:
				del linedict[hostHeadersDictNum]
			for x in range(len(linedict)):
				newfile.write(linedict[x])
			linenum = 0
			linedict = []
			continue
		if 'Nmap scan report for ' in line:
			hostidLine = line.split()
			if enginfo["type"] == "ext" and len(hostidLine) > 5:
				hostid = hostidLine[5]
				hostid = hostid.strip("()")
			else:
				hostid = hostidLine[4]
		if 'Not shown:' in line and 'tcp ports' in line:
			hostPortsDictNum = linenum
			hostPortsLine = line.split()
			hostPorts = int(hostPortsLine[2])
		if 'PORT' in line and 'STATE' in line and 'SERVICE' in line:
			hostHeadersDictNum = linenum
		if '53/tcp' in line and 'open' in line and 'tcpwrapped' in line:
			del linedict[linenum]
			hostPorts = hostPorts+1
			hostPorts = str(hostPorts)
			hostPortsLine[2] = hostPorts
			hostPortsLine.append('\n')
			FinalHostPortsLine = ' '.join(hostPortsLine)
			linedict[hostPortsDictNum] = FinalHostPortsLine	
			continue
		if 'open' in line and 'ssl' in line: #Check for TLS/SSL based services, add to a scope file if present
			tlsPortLine = line.split()
			tlsPort = tlsPortLine[0]
			tlsPort = tlsPort.strip("/tcp")
			tlsService = hostid+":"+tlsPort+"\n"
			with open(tlsFilename) as tlsfilecheck:
				if tlsService not in tlsfilecheck.read():
					tlsfile.write(tlsService)
		if 'open' in line and 'http' in line: #Check for HTTP/HTTPS based services, add to a scope file if present
			if 'https' in line or 'ssl/http' in line:
				httpsPortLine = line.split()
				httpsPort = httpsPortLine[0]
				httpsPort = httpsPort.strip("/tcp")
				if httpsPort == "443":
					httpsService = "https://"+hostid+"\n"
				else:
					httpsService = "https://"+hostid+":"+httpsPort+"\n"
				with open(httpFileName) as httpfilecheck:
					if httpsService not in httpfilecheck.read():
						httpfile.write(httpsService)
			else:
				httpPortLine = line.split()
				httpPort = httpPortLine[0]
				httpPort = httpPort.split("/tcp")
				if httpPort[0] == "80":
					httpService = "http://"+hostid+"\n"
				else:
					httpService = "http://"+hostid+":"+httpPort[0]+"\n"
				with open(httpFileName) as httpfilecheck:
					if httpService not in httpfilecheck.read():
						httpfile.write(httpService)
		linenum = linenum+1	
print("Nmap file parsed successfully and saved as: "+outputFilename)