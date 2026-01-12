import docker
import glob
import re
import subprocess
import os
import argparse
import time
from lib import assets
from termcolor import colored
from configparser import ConfigParser
from datetime import date
from datetime import datetime
from pathlib import Path
from prompt_toolkit import print_formatted_text, HTML, PromptSession, Application
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from urllib.request import urlretrieve
client = docker.from_env()
config_object = ConfigParser()
config_object.read("./config.ini")
global_config = config_object['GLOBAL']
curreng_object = ConfigParser()
today = date.today()
now = datetime.now()

#Header
usage_text = 'python emmett.py'
example_text = '''Example:
python emmett.py (Standard run)
python emmett.py --setup (Perform full setup)
python emmett.py --setup --no-docker (Perform setup without any Docker actions)
python emmett.py -u (Update current Emmett images)'''
parser = argparse.ArgumentParser(usage=usage_text, epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)

#Arguments
parser.add_argument("-u", "--update", help="Update existing Emmett image OS.\n", action="store_true")
parser.add_argument("--vpn-only", help="Boot Emmett with only VPN active, no engagement.\n", action="store_true")
parser.add_argument("--setup", help="Perform initial setup.\n", action="store_true")
parser.add_argument("--no-pull", help="Do not pull new kali image.\n", action="store_true")
parser.add_argument("--no-image", help="Do not create an Emmett image.\n", action="store_true")
parser.add_argument("--no-docker", help="Do not perform any Docker actions (same as running --no-image and --no-pull).\n", action="store_true") 
parser.add_argument("--no-burp", help="Do not download burpsuite JAR file\n", action="store_true")
parser.add_argument("--no-startup", help="Do not create startup script.\n", action="store_true")
parser.add_argument("--no-bat", help="Do not create bat file.\n", action="store_true")
parser.add_argument("--uninstall", help="Uninstall Emmett Assets.\n", action="store_true")
parser.add_argument("--client", help="Provide Client Name for Engagement.\n")
parser.add_argument("--eng_dir", help="Provide Client Directory for Engagement.\n")

args = parser.parse_args()

def main(ClientName, DirectoryName):
	print("{}".format(colored(DirectoryName+" Engagement Loaded Successfully.\n", "green")))
	#Initiate Docker
	DirectoryNameList = DirectoryName.split("_")
	StartDate = DirectoryNameList[0]+"_"+DirectoryNameList[1]+"_"+DirectoryNameList[2]
	AbsoluteDirectoryName = "../Clients/"+DirectoryName
	AbsoluteDirectoryName = Path.cwd() / AbsoluteDirectoryName
	AbsoluteDirectoryName = str(AbsoluteDirectoryName)
	#Getting shared folder locations and intialising VPN and initial Kali containers
	AbsoluteBuildName = Path.cwd() / "build/"
	AbsoluteBuildName = str(AbsoluteBuildName)
	GlobalConfigBuildName = AbsoluteBuildName + "/../config.ini"
	AbsoluteEmmettBuildName = AbsoluteBuildName + "/Emmett/shared"
	AbsoluteDeLoreanBuildName = AbsoluteBuildName + "/DeLoreans/shared"
	DocumentsVolume = AbsoluteDirectoryName+":/root/Documents"
	EmmettBuildVolume = AbsoluteEmmettBuildName+":/root/shared/"
	DeLoreansBuildVolume = AbsoluteDeLoreanBuildName+":/root/shared/"
	ConfigFileName = AbsoluteDirectoryName + "/data/emmett_config.ini" #Config file location
	TLSHostFileCheck = AbsoluteDirectoryName+"/data/tls_hosts.txt"
	TLSHostFileCheck = Path.cwd() / TLSHostFileCheck
	HTTPHostFileCheck = AbsoluteDirectoryName+"/data/http_hosts.txt"
	DirbCounter = 0
	KaliCounter = 1
	NiktoCounter = 0
	TCPNmapCounter = 0
	UDPNmapCounter = 0
	SSLCounter = 0
	ParzivalCounter = 0
	LivehostsCounter = 0
	WpscanCounter = 0
	InitialKaliName = 'Kali%s' % KaliCounter
	#Save Previous Engagement
	config_object.set('GLOBAL', 'preveng', DirectoryName)
	with open(GlobalConfigBuildName, 'w') as configfile:
		config_object.write(configfile)
	curreng_object.read(ConfigFileName)
	enginfo = curreng_object['ENGINFO']
	AutoEng_Config = curreng_object['AUTOENG']
	try:
		EmmettContainer = client.containers.run("emmett", detach=True, remove=True, devices=["/dev/net/tun"], cap_add=["NET_ADMIN"], privileged=False, name="Emmett", labels=["Emmett"], ports={'8118':'8118'}, volumes=[EmmettBuildVolume])
	except docker.errors.APIError:
		pass
	try:
		globals()['KaliContainer%s' % KaliCounter] = client.containers.run("delorean", detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=InitialKaliName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
	except docker.errors.APIError:
		pass

	KaliInput = input("Would You Like To Connect To A Kali Box? (Y/N Default:N): ")
	KaliInput = KaliInput.replace(" ", "")
	KaliInput = KaliInput.lower()
	if KaliInput == "y":
		if os.name == 'nt':
			KaliExec = subprocess.run("start cmd.exe /c docker exec -it "+InitialKaliName+" bash -i", shell=True)
		else:
			print("Copy/Paste \"docker exec -it "+InitialKaliName+" bash -i\" Into a New Terminal Window.")

	if enginfo["burp"] == "on": #Run Burp if config file is set to autorun burp on engagement start
		subprocess.Popen(['java', '-jar', '.\\lib\\burpsuite.jar', '--project-file='+AbsoluteDirectoryName+'\\data\\burpsuite.burp'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
	
	#CLI Prompt
	cliSession = PromptSession()
	cliCompleter = NestedCompleter.from_nested_dict({ #Autocomplete setup
		'add': {
			'scope': None
		},
		'connect': None,
		'create': {
			'container': {
				'emmett': None,
				'kali': None
			},
			'scope': None
		},
		'edit': {
			'engagement': None,
			'scope': {
				'http': None,
				'main': None,
				'tls': None
			}
		},
		'exit': None,
		'help': None,
		'kill': {
			'container': {
				'all': None
			},
			'autoengagement': None
		},
		'run': {
			'autoengagement': {
				'forcessl':None
			},
			'burp': None,
			'dirb': None,
			'nikto': None,
			'nmap': {
				'tcp': {
					'no-ping': None
				},
				'udp': {
					'no-ping': None
				}
			},
			'parzival': None,
			'testssl': None,
			'livehosts': None,
			'wpscan': None
		},
		'show': {
			'scope': {
				'http': None,
				'main': None,
				'tls' : None
			},
			'sessions': None,
			'status': None
		},
		'tail': None
	})
	MasterInput = ""
	while True: #Prompt Loop
		ContainerList = client.containers.list(filters={"label":"Emmett"})
		MasterInput = cliSession.prompt("Emmett> ", completer=cliCompleter, auto_suggest=AutoSuggestFromHistory())
		MasterInput = MasterInput.split()
		if not MasterInput:
			MasterInput = ""
		else: #Start of Commands List
			if MasterInput[0] == "help" or MasterInput[0] == "h"or MasterInput[0] == "?": #Help output
				print("""COMMAND LIST:
  add scope - Add new hosts to the existing scope.
     Usage: add scope
            add scope [hosts]

  connect - Open a bash session on container.
     Usage: connect [container]

  create - Create new resources.
     Usage: create [options]
     OPTIONS:
       container - Create new containers.
          emmett - Create new VPN proxy container (this is unique, only 1 can run at a time).
          kali - Create new persistent Kali container.
       scope - Overwrite current scope file with new.

  edit - Alter engagement areas.
     Usage: edit [option]
     OPTIONS:
       engagement - Open settings screen to alter engagement configuration.
       scope - Open main scope file in notepad for editing.
       scope [scope type] - Open chosen engagement scope file for editing.
       SCOPE TYPES:
         http
         main
         tls

  exit - Kill all Emmett jobs and exit.

  help - Show this screen.

  kill - Kill containers
     Usage: kill [option]
     OPTIONS:
       autoengagement - Kill all running containers associated with AutoEngagement.
       container [container] - Kill selected Emmett container.
       container all - Kill all Emmett containers.

  run - Execute a tool against scope file. Outputs will be given in the engagements output folder.
     Usage: run [tool]
     TOOLS:
       autoengagement - Runs AutoEngagement tool in new window.
       burp - Run burpsuite with current engagement project.
       dirb - Runs Dirb against the http scope.
       livehosts - Runs nmap check for livehosts and creates output file.
       nikto [Optional Number of hosts per scan (Default 5)] - Runs Nikto against the http scope.       
       nmap - Runs either full TCP or common UDP nmap scan based on arguments used with command. 
       parzival - Runs Parzival nmap script to remove port 53 false positive from an output file from scans done over certain VPNs.
       testssl - Runs testssl, saves output and runs through ezmodessl.
       wpscan - Runs wpscan against the http scope.

  show - Show data regarding engagement and containers.
     Usage: show [options]
     OPTIONS:
       scope - Output main engagement scope file.
       scope [scope type] - Output chosen engagement scope file.
       SCOPE TYPES:
         http
         main
         tls
       sessions - Open new terminal window showing active Emmett containers.
       status [container] - Show current terminal output of chosen container.

  tail - Show continous terminal output of chosen container.
     Usage: tail [container]
				""")
			if re.search('add', MasterInput[0], re.IGNORECASE): #Add to scope existing scope file
				if len(MasterInput) == 1:
					print("""COMMAND HELP:
  Description - Add new hosts to the existing scope.
  Usages: add scope
          add scope [hosts]
						""")
				else:
					if re.search('scope', MasterInput[1], re.IGNORECASE):
						DirectoryLocation = "../Clients/"+DirectoryName	
						HostFileLocation = DirectoryLocation + "/data/hosts.txt"
						HostFile = open(HostFileLocation, 'a')
						CurrentEngagementScopeFile = open(HostFileLocation, 'r')
						CurrentEngagementScope = CurrentEngagementScopeFile.readlines()
						ExistingHostCheck = False
						ScopeChangeSuccessCheck = False				
						if len(MasterInput) == 2:
							print("Enter/Paste Your Testing Scope. {} (Windows) or ".format(colored("Ctrl-Z", "yellow"))+"{} (Linux) on a New Line to Save.".format(colored("Ctrl-D", "yellow")))
							EngagementScope = []
							while True:
							    try:
							        line = input()
							        if line:
							        	if re.match(assets.scope_regex, line): #Checking user input for bad characters
							        		for currentline in CurrentEngagementScope:
							        			if line in currentline:
							        				ExistingHostCheck = True
							        		if ExistingHostCheck == False:
							        	 		EngagementScope.append(line)
							        	 		ScopeChangeSuccessCheck = True
							        		else:
							        			print("{}: The host provided in the previous line already exists in the scope file.".format(colored("ERROR", "red", attrs=["bold"])))
							        			ExistingHostCheck = False
							        	else:
							        		print("{}: The Previous Line Contained Invalid Characters And Will Be Omitted From The Scope File. Please Add Manually Afterwards If Required.".format(colored("ERROR", "red", attrs=["bold"])))
							    except EOFError:
							        break
							for x in range(len(EngagementScope)):
							    HostFile.write(EngagementScope[x]+"\n")
							HostFile.close()
							print("{}".format(colored("Scope File Successfully Created.", "green")))	

						if len(MasterInput) >= 3:
							MasterInput.remove("scope")
							MasterInput.remove("add")
							for x in range(len(MasterInput)):
								if re.match(assets.scope_regex, MasterInput[x]):
									for currentline in CurrentEngagementScope:
										if MasterInput[x] in currentline:
											ExistingHostCheck = True
									if ExistingHostCheck == False:
										HostFile.write(MasterInput[x]+"\n")
										ScopeChangeSuccessCheck = True
									else:
										print("{}: The host ".format(colored("ERROR", "red", attrs=["bold"]))+MasterInput[x]+" already exists in the scope file.")
										ExistingHostCheck = False
								else:
									print("{}: The host ".format(colored("ERROR", "red", attrs=["bold"]))+MasterInput[x]+" could not be added to the scope file due to invalid characters being detected.")
							HostFile.close()
							if ScopeChangeSuccessCheck == True:
								print("{}".format(colored("Scope File Successfully Updated.", "green")))	

			if re.search('connect', MasterInput[0], re.IGNORECASE): #Connect to an Emmett container with a bash session
				if len(MasterInput) == 1:
					print("""COMMAND HELP:
  Description - Open a bash session on container.
  Usage: connect [container]
						""")
				else:
					print("Attempting to Connect You to "+"{}".format(colored(MasterInput[1], "yellow")))
					ConnectContainerName = MasterInput[1].capitalize()
					try: 
						if os.name == "nt":
							subprocess.run("start cmd.exe /c docker exec -it "+ConnectContainerName+" bash -i", shell=True)
						else:
							print("Copy/Paste \"docker exec -it "+ConnectContainerName+" bash -i\" Into a New Terminal Window.")
					except:
						print("{}: Unable to Connect to ".format(colored("ERROR", "red", attrs=["bold"]))+"{}".format(colored(MasterInput[1], "yellow")))

			if re.search('create', MasterInput[0], re.IGNORECASE): #Creating new containers or scope for engagement.
				if len(MasterInput) == 1:
					print("""COMMAND HELP:
  Description - Create new resources
  Usage: create [options]
  OPTIONS:
     container - Create containers.
        emmett - Create new VPN proxy container (this is unique, only 1 can run at a time).
        kali - Create new persistent Kali container.
     scope - Overwrite current scope file with new.
						""")
				else:
					if re.search('container', MasterInput[1], re.IGNORECASE):
						if len(MasterInput) == 2:
							print("""
  Description: Create containers.
  Usage: create container [container]
  CONTAINER TYPES:
     emmett - Create new VPN proxy container (this is unique, only 1 can run at a time).
     kali - Create new persistent Kali container.
								""")
						else:
							if re.search('emmett', MasterInput[2], re.IGNORECASE):
								EmmettContainer = client.containers.run("emmett", detach=True, remove=True, devices=["/dev/net/tun"], cap_add=["NET_ADMIN"], privileged=False, name="Emmett", labels=["Emmett"], ports={'8118':'8118'}, volumes=[EmmettBuildVolume])
								print("Starting {} Container".format(colored("Emmett", "yellow")))
							if MasterInput[2] == 'kali':
								KaliCounter = KaliCounter+1
								NewKaliName = 'Kali%s' % KaliCounter
								globals()['KaliContainer%s' % KaliCounter] = client.containers.run("delorean", detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=NewKaliName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
								print("Starting Kali container named {}".format(colored(NewKaliName, "yellow")))
							if re.search('kali-priv', MasterInput[2], re.IGNORECASE):
								KaliCounter = KaliCounter+1
								NewKaliName = 'Kali%s-priv' % KaliCounter
								globals()['KaliContainer%s' % KaliCounter] = client.containers.run("delorean", detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=True, name=NewKaliName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
								print("Starting Privileged Kali container named {}".format(colored(NewKaliName, "yellow")))

					if re.search('scope', MasterInput[1], re.IGNORECASE):
						DirectoryLocation = "../Clients/"+DirectoryName
						print("{}: THIS WILL OVERWRITE ANY EXISTING SCOPE FOR THIS ENGAGEMENT!".format(colored("WARNING", "red", attrs=["bold"])))
						while True:
							NewScopeCheckInput = input("Would You Like to Continue? (Y/N Default:N)") #Prompt to ask user if they want to continue to overwrite scope.
							NewScopeCheckInput = NewScopeCheckInput.replace(" ", "")
							NewScopeCheckInput = NewScopeCheckInput.lower()
							if NewScopeCheckInput in ("y","n",""):
								break
						if NewScopeCheckInput == "y":
							print("Enter/Paste Your Testing Scope. {} (Windows) or ".format(colored("Ctrl-Z", "yellow"))+"{} (Linux) on a New Line to Save.".format(colored("Ctrl-D", "yellow")))
							HostFileLocation = DirectoryLocation + "/data/hosts.txt"
							HTTPHostFileLocation = DirectoryLocation + "/data/http_hosts.txt"
							HostFile = open(HostFileLocation, 'w')
							HTTPHostFile = open(HTTPHostFileLocation, 'w')
							EngagementScope = []
							HTTPEngagementScope = []
							while True:
								try:
									line = input()
									if line:
										if re.match(assets.scope_regex, line): #Checking user input for bad characters
											if re.match(assets.url_regex, line): #Checking if user input is a URL
												if line not in HTTPEngagementScope:
													HTTPEngagementScope.append(line)
													HTTPDomain = line.split('/')
													HTTPDomain = HTTPDomain[2]
													if HTTPDomain not in EngagementScope:
														EngagementScope.append(HTTPDomain)
											else:
												if line not in EngagementScope:
													EngagementScope.append(line)
										else:
											print("{}: The Previous Line Contained Invalid Characters And Will Be Omitted From The Scope File. Please Add Manually Afterwards If Required.".format(colored("ERROR", "red")))
								except EOFError:
									break

							for x in range(len(EngagementScope)):
							    HostFile.write(EngagementScope[x]+"\n")
							for x in range(len(HTTPEngagementScope)):
								HTTPHostFile.write(HTTPEngagementScope[x]+"\n")

							HTTPHostFile.close()
							HostFile.close()
							print("{}".format(colored("Scope File Successfully Created.", "green")))							
						else:
							print("No Changes Made to Existing Scope.")

			if re.search('edit', MasterInput[0], re.IGNORECASE): #Editing engagement config screen or editing scope.
				if len(MasterInput) == 1:
					print("""COMMAND HELP:
  Description - Alter engagement areas.
  Usage: edit [option]
  OPTIONS:
     engagement - Open settings screen to alter engagement configuration.
     scope - Open scope file in notepad for editing.
     scope [scope type] - Open chosen engagement scope file for editing.
     SCOPE TYPES:
       http
       main
       tls
						""")
				else:
					if re.search('engagement', MasterInput[1], re.IGNORECASE):
						EngagementConfigEntries = ["client", "type", "burp"]
						print("\nCurrent Engagement Configuration:")
						print("[1] Client: {}".format(colored(enginfo["client"], "yellow")))
						print("[2] Engagement Type: {}".format(colored(enginfo["type"], "yellow")))
						print("[3] Burp on Boot: {}".format(colored(enginfo["burp"], "yellow")))
						print("[4] AutoEngagment State: {}".format(colored(AutoEng_Config['state'], "yellow"))+"\n")
						while True:
							EngagementEditInput = input("Choose Which Engagement Configuration You Want To Change Or Leave Blank To Exit: ")
							EngagementEditInput = EngagementEditInput.replace(" ", "")
							EngagementEditInput = EngagementEditInput.lower()
							if EngagementEditInput == "":
								break
							else:
								try:
									EngagementEditInput = int(EngagementEditInput)
									EngagementEditInput = EngagementEditInput-1
								except:
									print("{}: Unrecognised Input, Must Be An Integer Or Blank.".format(colored("ERROR", "red", attrs=["bold"])))
								else:
									break
						if EngagementEditInput == 0: #Updating client name and associated folders
							print("\n{}: Updating Client Name Can Result in a Restart of All Emmett Related Containers and a Renaming to the Associated Engagement Directory.\n".format(colored("WARNING", "red", attrs=["bold"])))
							while True:
								NewEngagementEditInput = input("Enter New Client Name for Current Engagement:") 
								if NewEngagementEditInput:
									if re.match(assets.regex, NewEngagementEditInput): #Checking user input for bad characters
										break
									else:
										print("{}: Your Input Contained Invalid Characters.".format(colored("ERROR", "red", attrs=["bold"])))

							NewEngagementEditInput = NewEngagementEditInput.lower()
							curreng_object.set('ENGINFO', 'client', NewEngagementEditInput) #Update Config File
							with open(ConfigFileName, 'w') as configfile:
								curreng_object.write(configfile)
							print("Client Name Successfully Updated to "+"{}".format(colored(NewEngagementEditInput, "yellow")))

							while True:
								NewEngagementEditRename = input("Would You Like Emmett to Rename the Associated Engagement Directory? (Y/N Default:Y)") #Prompt to ask user if they want to update directory name.
								NewEngagementEditRename = NewEngagementEditRename.replace(" ", "")
								NewEngagementEditRename = NewEngagementEditRename.lower()
								if NewEngagementEditRename in ("y","n",""):
									break
							if NewEngagementEditRename == "n":
								print("Directory Name Has Been Preserved.")
								break
							else:
								NewEngagementEditInput = NewEngagementEditInput.replace(" ", "_") #Updating Directory Name, killing all current containers and restarting main function.
								OldDirectoryName = AbsoluteDirectoryName
								DirectoryName = StartDate+"_"+NewEngagementEditInput
								AbsoluteDirectoryName = "../Clients/"+StartDate+"_"+NewEngagementEditInput
								os.rename(OldDirectoryName, AbsoluteDirectoryName)
								ClientName = NewEngagementEditInput
								config_object.set("GLOBAL", "curreng", DirectoryName)
								config_object.set("GLOBAL", "preveng", DirectoryName)
								with open(GlobalConfigBuildName, 'w') as configfile:
									config_object.write(configfile)

								print("Engagement Directory Renamed.\nRestarting Emmett.\n")
								for x in ContainerList: #Breaking up ContainerList entries to be just container IDs and killing the associated containers
									x = str(x)
									x = x.replace("<Container: ", "")
									x = x.replace(">", "")
									subprocess.run(['docker', 'container', 'kill', x], stdout=subprocess.DEVNULL)

								main(ClientName, DirectoryName)	

						if EngagementEditInput == 1: #Updating engagement type configuration.
							while True:
								NewEngagementEditInput = input("What is the Engagement Type? (Web/Ext/API):")
								NewEngagementEditInput = NewEngagementEditInput.replace(" ","")
								NewEngagementEditInput = NewEngagementEditInput.lower()
								if NewEngagementEditInput in ("web","ext","api"):
									curreng_object.set('ENGINFO', 'type', NewEngagementEditInput) #Update Config File
									with open(ConfigFileName, 'w') as configfile:
										curreng_object.write(configfile)
										print("Engagement Type Successfully Updated to "+"{}".format(colored(NewEngagementEditInput, "yellow")))
										break

						if EngagementEditInput == 2: #Updating configuration is burp should auto open on boot.
							if enginfo["burp"] == "on":
								curreng_object.set('ENGINFO', 'burp', 'off') #Update Config File
								with open(ConfigFileName, 'w') as configfile:
									curreng_object.write(configfile)
									print("Burp on Boot Mode Changed to {}.".format(colored("OFF", "yellow")))
							else:
							 if enginfo["burp"] == "off":
									curreng_object.set('ENGINFO', 'burp', 'on') #Update Config File
									with open(ConfigFileName, 'w') as configfile:
										curreng_object.write(configfile)
										print("Burp on Boot Mode Changed to {}.".format(colored("ON", "yellow")))

						if EngagementEditInput == 3: #Clearing AutoEng Status
							while True:
								NewEngagementEditInput = input("Would you like to reset AutoEngagement state? (Y/N Default:Y)")
								NewEngagementEditInput = NewEngagementEditInput.replace(" ", "")
								NewEngagementEditInput = NewEngagementEditInput.lower()
								if NewEngagementEditInput in ("y","n",""):
									break
							if NewEngagementEditInput == "n":
								print("AutoEngagement state has been preserved.")
								break
							else:
								curreng_object.set("AUTOENG", "state", "Not Started")
								with open(ConfigFileName, 'w') as configfile:
									curreng_object.write(configfile)
									print("{}".format(colored("AutoEngagement state reset.", "yellow")))									
					if MasterInput[1] == "scope":
						DirectoryLocation = "../Clients/"+DirectoryName
						if len(MasterInput) == 2: #Opening scope file in notepad for editing
							HostFileLocation = DirectoryLocation + "/data/hosts.txt"
						else:
							if re.search('http', MasterInput[2], re.IGNORECASE):
								HostFileLocation = DirectoryLocation + "/data/http_hosts.txt"
							if re.search('main', MasterInput[2], re.IGNORECASE):
								HostFileLocation = DirectoryLocation + "/data/hosts.txt"
							if re.search('tls', MasterInput[2], re.IGNORECASE):
								HostFileLocation = DirectoryLocation + "/data/tls_hosts.txt"
						try:
							subprocess.Popen(['notepad', HostFileLocation], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
							del HostFileLocation
						except OSError:
							try:
								subprocess.Popen(['write', HostFileLocation], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
								del HostFileLocation
							except:
								print("{}: No notes application detected.".format(colored('ERROR', 'red', attrs=["bold"])))
								del HostFileLocation
						except UnboundLocalError:
							print("{}: Incorrect scope type submitted.".format(colored('ERROR', 'red', attrs=["bold"])))

			
			if re.search('exit', MasterInput[0], re.IGNORECASE): #Command for exiting Emmett CLI
				sessions_exit()
				exit()					

			if re.search('kill', MasterInput[0], re.IGNORECASE): #Command for killing containers
				if len(MasterInput) == 1:
					print("""COMMAND HELP:
  Description - Kill containers
  Usage: kill [option]
     autoengagement - Kill all running ocntainers associated with AutoEngagement.
     kill [container] - Kill selected Emmett container.
     kill all - Kill all Emmett containers.
						""")
				else:
					if re.search('all', MasterInput[1], re.IGNORECASE):
						print("Stopping all containers.")
						for x in ContainerList: #Breaking up ContainerList entries to be just container IDs and killing the associated containers
							x = str(x)
							x = x.replace("<Container: ", "")
							x = x.replace(">", "")
							subprocess.run(['docker', 'container', 'kill', x], stdout=subprocess.DEVNULL)			
					else:
						if re.search('autoengagement', MasterInput[1], re.IGNORECASE):
							print("Stopping all AutoEngagement containers.")
							ContainerListAutoEng = client.containers.list(filters={"label":"Engagement"})
							for x in ContainerListAutoEng:
								x = str(x)
								x = x.replace("<Container: ", "")
								x = x.replace(">", "")
								subprocess.run(['docker', 'container', 'kill', x], stdout=subprocess.DEVNULL)
						else: 
							ContainerKill = MasterInput[1]
							ContainerKill = ContainerKill.capitalize()
							KillProcess = subprocess.run(['docker', 'container', 'kill', ContainerKill], capture_output=True, text=True)
							ContainerKillCheck = KillProcess.stderr
							if ContainerKillCheck == "":
								print("Successfully stopped container {}".format(colored(MasterInput[1], "yellow")))
							else:
								print("{}: ".format(colored("ERROR", "red", attrs=["bold"]))+ContainerKillCheck)

			if re.search('run', MasterInput[0], re.IGNORECASE): #Run a tool
				now = datetime.now()
				if len(MasterInput) == 1:
					print("""COMMAND HELP:
  Description - Execute a tool against scope file. Outputs will be given in the engagements output folder.
  Usage: run [tool]
  TOOL LIST:
    autoengagement - Runs all tools.
    burp
    dirb [Optional Number of hosts per scan (Default 5)]
    nikto [Optional Number of hosts per scan (Default 5)]
    livehosts - Runs nmap check for livehosts and creates output file.
    nmap
    testssl 
    wpscan [Optional Number of hosts per scan (Default 5)]
						""")
				else:
					if re.search('autoengagement', MasterInput[1], re.IGNORECASE):
						EngagementCommand = "start cmd.exe /c python ./lib/autoengagement.py --client \""+ClientName+"\" --engdir \""+AbsoluteDirectoryName+"\""
						subprocess.run(EngagementCommand, shell=True)

					if re.search('burp', MasterInput[1], re.IGNORECASE):
						subprocess.Popen(['java', '-jar', '.\\lib\\burpsuite.jar', '--project-file='+AbsoluteDirectoryName+'\\data\\burpsuite.burp'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

					if re.search('dirb', MasterInput[1], re.IGNORECASE):
						if os.stat(HTTPHostFileCheck).st_size != 0:
							with open(HTTPHostFileCheck, 'r') as file:
								HTTPHostRead = file.read()
								HTTPHostRead = HTTPHostRead.split("\n")
								if len(MasterInput) > 2: #Checking if user inputted a manual number of hosts per container.
									try:
										DirbMaxHostNum = int(MasterInput[2])
									except:
										print("{}: Number of hosts must be an integer.".format(colored("ERROR", "red", attrs=["bold"])))
										continue
								else:
									DirbMaxHostNum = 5 #Default number of hosts per container.
								HTTPHostRead = [x for x in HTTPHostRead if x] #Remove any empty entries
								if len(HTTPHostRead) > DirbMaxHostNum:
									DirbSubList = [HTTPHostRead[i:i + DirbMaxHostNum] for i in range(0, len(HTTPHostRead), DirbMaxHostNum)] #Breaking up list into sublists.									
									for i in DirbSubList:
										DirbCounter = DirbCounter+1
										DirbNewName = 'Dirb%s' % DirbCounter
										DirbFileName = DirbNewName+"_output_"+now.strftime("%d%m%y_%H%M")+".txt"
										DirbScopeFileName = AbsoluteDirectoryName+'/data/'+DirbNewName+'_hosts.txt'
										with open(DirbScopeFileName, 'w') as file:
											for line in i:
												file.write("%s\n" % line)
										DirbHostNum = len(i)
										DirbHostNum = str(DirbHostNum)
										DirbCommand = "/bin/bash -c \"mv /root/Documents/data/"+DirbNewName+"_hosts.txt /tmp/ && python /root/shared/tools/dirbloop.py -f /tmp/"+DirbNewName+"_hosts.txt -o /root/Documents/output/http/"+DirbFileName+"\""
										globals()['DirbContainer%s' % DirbCounter] = client.containers.run("delorean", DirbCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=DirbNewName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
										print("\nDirb has been executed in container for "+DirbHostNum+" hosts from the http scope file. When complete output can be found within {}.".format(colored("output/http/"+DirbFileName, "yellow")))
								else:
									print("working")
									DirbCounter = DirbCounter+1
									DirbNewName = 'Dirb%s' % DirbCounter
									DirbFileName = "dirb_output_"+now.strftime("%d%m%y_%H%M")+".txt"
									DirbCommand = "/bin/bash -c \"python /root/shared/tools/dirbloop.py -f /root/Documents/data/http_hosts.txt -o /root/Documents/output/http/"+DirbFileName+"\""
									globals()['DirbContainer%s' % DirbCounter] = client.containers.run("delorean", DirbCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=DirbNewName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
									print("\nDirb has been executed in container for all hosts in http scope file. When complete output can be found within {}.".format(colored("output/http/"+DirbFileName, "yellow")))

					if re.search('livehosts', MasterInput[1], re.IGNORECASE):
						LivehostsCounter = LivehostsCounter+1
						NewLivehostsName = 'Livehosts%s' % LivehostsCounter
						globals()['LivehostsContainer%s' % LivehostsCounter] = client.containers.run("delorean", "/bin/sh -c \"nmap -p- --open -iL /root/Documents/data/hosts.txt -oG - | grep '/open' | awk '{ print $2 }' > /root/Documents/output/nmap/livehosts.txt\"", detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=NewLivehostsName, labels=["Emmett"], volumes=[DocumentsVolume])
						print("\nNmap command \"{}\" has been executed in container ".format(colored("nmap -p- --open -iL /root/Documents/data/hosts.txt", "yellow"))+"{}".format(colored(NewLivehostsName, "yellow"))+". When complete outputs can be found within {}.".format(colored("output/nmap/livehosts.txt", "yellow")))		

					if re.search('nikto', MasterInput[1], re.IGNORECASE):
						if os.stat(HTTPHostFileCheck).st_size != 0:
							with open(HTTPHostFileCheck, 'r') as file:
								HTTPHostRead = file.read()
								HTTPHostRead = HTTPHostRead.split("\n")
								if len(MasterInput) > 2: #Checking if user inputted a manual number of hosts per container.
									try:
										NiktoMaxHostNum = int(MasterInput[2])
									except:
										print("{}: Number of hosts must be an integer.".format(colored("ERROR", "red", attrs=["bold"])))
										continue
								else:
									NiktoMaxHostNum = 5 #Default number of hosts per container.
								HTTPHostRead = [x for x in HTTPHostRead if x] #Remove any empty entries
								if len(HTTPHostRead) > NiktoMaxHostNum:
									NiktoSubList = [HTTPHostRead[i:i + NiktoMaxHostNum] for i in range(0, len(HTTPHostRead), NiktoMaxHostNum)] #Breaking up list into sublists.
									for i in NiktoSubList:
										NiktoCounter = NiktoCounter+1
										NiktoNewName = 'Nikto%s' % NiktoCounter
										NiktoFileName = NiktoNewName+"_output_"+now.strftime("%d%m%y_%H%M")+".txt"
										NiktoScopeFileName = AbsoluteDirectoryName+'/data/'+NiktoNewName+'_hosts.txt'
										with open(NiktoScopeFileName, 'w') as file:
											for line in i:
												file.write("%s\n" % line)
										NiktoHostNum = len(i)
										NiktoHostNum = str(NiktoHostNum)
										NiktoCommand = "/bin/bash -c \"mv /root/Documents/data/"+NiktoNewName+"_hosts.txt /tmp/ && nikto -h /tmp/"+NiktoNewName+"_hosts.txt |& tee /root/Documents/output/http/"+NiktoFileName+"\""
										globals()['NiktoContainer%s' % NiktoCounter] = client.containers.run("delorean", NiktoCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=NiktoNewName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
										print("\nNikto command \"{}\" has been executed for ".format(colored("nikto -h /root/Documents/data/http_hosts.txt", "yellow"))+NiktoHostNum+" hosts from the scope in container "+"{}".format(colored(NiktoNewName, "yellow"))+". When complete output can be found within {}.".format(colored("output/http/"+NiktoFileName, "yellow")))
								else:
									NiktoCounter = NiktoCounter+1
									NiktoNewName = 'Nikto%s' % NiktoCounter
									NiktoFileName = NiktoNewName+"_output_"+now.strftime("%d%m%y_%H%M")+".txt"
									NiktoCommand = "/bin/bash -c \"nikto -h /root/Documents/data/http_hosts.txt >> /root/Documents/output/http/"+NiktoFileName+"\""
									globals()['NiktoContainer%s' % NiktoCounter] = client.containers.run("delorean", NiktoCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=NiktoNewName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
									print("\nNikto command \"{}\" has been executed in container ".format(colored("nikto -h /root/Documents/data/http_hosts.txt", "yellow"))+"{}".format(colored(NiktoNewName, "yellow"))+". When complete output can be found within {}.".format(colored("output/http/"+NiktoFileName, "yellow")))
	

					if re.search('nmap', MasterInput[1], re.IGNORECASE) and len(MasterInput) == 2:
						print("""COMMAND HELP:
  Description - Executes nmap scans against scope.
  Usage: run nmap [scan type]
  SCAN TYPES:
    tcp - Runs a full TCP port scan with version scan argument enabled.
    tcp no-ping - Runs a full TCP port scan with no ping argument enabled.
    udp - Runs a common UDP port scan
    udp no-ping - Runs a common UDP port scan with no ping argument enabled

All outputs saved to current client folder under ./output/nmap/ directory.
							""")

					if re.search('nmap', MasterInput[1], re.IGNORECASE) and len(MasterInput) == 3:
						if re.search('tcp', MasterInput[2], re.IGNORECASE):
							TCPNmapCounter = TCPNmapCounter+1
							TCPNewNmapName = 'Nmaptcp%s' % TCPNmapCounter
							TCPNmapFileName = "tcp_output_"+now.strftime("%d%m%y_%H%M")
							TCPNmapCommand = "/bin/bash -c \"nmap -sV -p- -iL /root/Documents/data/hosts.txt -v -oN /root/Documents/output/nmap/raw_outputs/tcp_raw.txt && python /root/shared/tools/parzival.py -f /root/Documents/output/nmap/raw_outputs/tcp_raw.txt -o /root/Documents/output/nmap/"+TCPNmapFileName+"\""
							globals()['TCPNmapContainer%s' % TCPNmapCounter] = client.containers.run("delorean", TCPNmapCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=TCPNewNmapName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
							print("\nNmap command \"{}\" has been executed in container ".format(colored("nmap -sV -p- -iL /root/Documents/data/hosts.txt", "yellow"))+"{}".format(colored(TCPNewNmapName, "yellow"))+". When complete output can be found within {}.".format(colored("output/nmap/"+TCPNmapFileName+".txt", "yellow")))

						if re.search('udp', MasterInput[2], re.IGNORECASE):
							UDPNmapCounter = UDPNmapCounter+1
							UDPNmapFileName = "udp_output_"+now.strftime("%d%m%y_%H%M")
							UDPNewNmapName = 'Nmapudp%s' % UDPNmapCounter
							UDPNmapCommand = "/bin/bash -c \"nmap -sU -iL /root/Documents/data/hosts.txt -v -oN /root/Documents/output/nmap/raw_outputs/udp_raw.txt && python /root/shared/tools/parzival.py -f /root/Documents/output/nmap/raw_outputs/udp_raw.txt -o /root/Documents/output/nmap/udp_output"+UDPNmapFileName+"\""
							globals()['UDPNmapContainer%s' % UDPNmapCounter] = client.containers.run("delorean", UDPNmapCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=UDPNewNmapName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
							print("\nNmap command \"{}\" has been executed in container ".format(colored("nmap -sU -iL /root/Documents/data/hosts.txt", "yellow"))+"{}".format(colored(UDPNewNmapName, "yellow"))+". When complete output can be found within {}.".format(colored("output/nmap/"+UDPNmapFileName+".txt", "yellow")))

					if re.search('nmap', MasterInput[1], re.IGNORECASE) and len(MasterInput) == 4:
						if re.search('tcp', MasterInput[2]) and re.search('no-ping', MasterInput[3]):
							TCPNmapCounter = TCPNmapCounter+1
							TCPNewNmapName = 'Nmaptcp%s' % TCPNmapCounter
							TCPNmapFileName = "tcp_output_"+now.strftime("%d%m%y_%H%M")
							TCPNmapCommand = "/bin/bash -c \"nmap -sV -Pn -p- -iL /root/Documents/data/hosts.txt -v -oN /root/Documents/output/nmap/raw_outputs/tcp_raw.txt && python /root/shared/tools/parzival.py -f /root/Documents/output/nmap/raw_outputs/tcp_raw.txt -o /root/Documents/output/nmap/"+TCPNmapFileName+"\""
							globals()['TCPNmapContainer%s' % TCPNmapCounter] = client.containers.run("delorean", TCPNmapCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=TCPNewNmapName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
							print("\nNmap command \"{}\" has been executed in container ".format(colored("nmap -sV -Pn -p- -iL /root/Documents/data/hosts.txt", "yellow"))+"{}".format(colored(TCPNewNmapName, "yellow"))+". When complete output can be found within {}.".format(colored("output/nmap/"+TCPNmapFileName+".txt", "yellow")))
					
					if re.search('nmap', MasterInput[1], re.IGNORECASE) and len(MasterInput) == 4:
						if re.search('udp', MasterInput[2]) and re.search('no-ping', MasterInput[3]):
							UDPNmapCounter = UDPNmapCounter+1
							UDPNmapFileName = "udp_output_"+now.strftime("%d%m%y_%H%M")
							UDPNewNmapName = 'Nmapudp%s' % UDPNmapCounter
							UDPNmapCommand = "/bin/bash -c \"nmap -sU -Pn -iL /root/Documents/data/hosts.txt -v -oN /root/Documents/output/nmap/raw_outputs/udp_raw.txt && python /root/shared/tools/parzival.py -f /root/Documents/output/nmap/raw_outputs/udp_raw.txt -o /root/Documents/output/nmap/udp_output"+UDPNmapFileName+"\""
							globals()['UDPNmapContainer%s' % UDPNmapCounter] = client.containers.run("delorean", UDPNmapCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=UDPNewNmapName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
							print("\nNmap command \"{}\" has been executed in container ".format(colored("nmap -sU -Pn -iL /root/Documents/data/hosts.txt", "yellow"))+"{}".format(colored(UDPNewNmapName, "yellow"))+". When complete output can be found within {}.".format(colored("output/nmap/"+UDPNmapFileName+".txt", "yellow")))
					
					if re.search('parzival', MasterInput[1], re.IGNORECASE):
						if len(MasterInput) < 3:
							print("""COMMAND HELP:
	Description - Executes Parzival script to parse an nmap output file to remove the port 53 issue created by scanning over certain VPNs. Input file must be within engagements output/nmap folder.
	Usage: run parzival [input filename] [output filename (optional)]
								""")
						if len(MasterInput) == 3:
							ParzivalInputFilename = MasterInput[2]
							ParzivalCounter = ParzivalCounter+1
							NewParzivalName = 'Parzival%s' % ParzivalCounter
							ParzivalCommand = '/bin/bash -c \"cd /root/Documents/output/nmap && python /root/shared/tools/parzival.py -f '+ParzivalInputFilename+'\"'
							globals()['ParzivalContainer%s' % ParzivalCounter] = client.containers.run("delorean", ParzivalCommand, detach=True, cap_add=["NET_ADMIN"], remove=True, network_mode="container:Emmett", privileged=False, name=NewParzivalName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
							print("\nParzival command \"{}".format(colored("python /root/shared/tools/parzival.py -f "+ParzivalInputFilename, "yellow"))+"\" has been executed in container {}.".format(colored(NewParzivalName, "yellow")))

						if len(MasterInput) == 4:
							ParzivalInputFilename = MasterInput[2]
							ParzivalOutputFilename = ' -o '+MasterInput[3] 
							ParzivalCounter = ParzivalCounter+1
							NewParzivalName = 'Parzival%s' % ParzivalCounter
							ParzivalCommand = '/bin/bash -c \"cd /root/Documents/output/nmap && python /root/shared/tools/parzival.py -f '+ParzivalInputFilename+ParzivalOutputFilename+'\"'
							globals()['ParzivalContainer%s' % ParzivalCounter] = client.containers.run("delorean", ParzivalCommand, detach=True, cap_add=["NET_ADMIN"], remove=True, network_mode="container:Emmett", privileged=False, name=NewParzivalName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
							print("\nParzival command \"{}".format(colored("python /root/shared/tools/parzival.py -f "+ParzivalInputFilename+ParzivalOutputFilename, "yellow"))+"\" has been executed in container {}".format(colored(NewParzivalName, "yellow"))+". When complete output can be found within {}.".format(colored("output/nmap/"+ParzivalOutputFilename, "yellow")))

					if re.search('testssl', MasterInput[1], re.IGNORECASE):
						SSLCounter = SSLCounter+1
						NewSSLName = 'Testssl%s' % SSLCounter
						SSLHTMLFileName = "tls_output_"+now.strftime("%d%m%y_%H%M")+".html"
						if TLSHostFileCheck.is_file():
							SSLCommand = "/bin/bash -c \"cd /root/Documents/output/tls/raw_outputs && testssl --warnings=batch --log --json --file ../../../data/tls_hosts.txt |& tee -a /tmp/"+SSLHTMLFileName+" && cat /tmp/"+SSLHTMLFileName+" | ansi2html > /root/Documents/output/tls/"+SSLHTMLFileName+" && /root/shared/EzModeSSL -d . -o ../"+ClientName+"\""
							globals()['SSLContainer%s' % SSLCounter] = client.containers.run("delorean", SSLCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=NewSSLName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
							print("\nTestSSL command \"{}\" has been executed in container ".format(colored("testssl --warnings=batch --log --json --file ../../../data/tls_hosts.txt", "yellow"))+"{}".format(colored(NewSSLName, "yellow"))+". When complete outputs can be found within {}.".format(colored("output/tls/", "yellow")))						
						else:
							print("\n{}: No TLS hosts file found, performing best effort scan using host file. For more accurate results run nmap to completion to generate a tls host file.".format(colored("WARNING", "red", attrs=["bold"])))
							SSLCommand = "/bin/bash -c \"cd /root/Documents/output/tls/raw_outputs && testssl --warnings=batch --log --json --file ../../../data/hosts.txt |& tee -a /tmp/"+SSLHTMLFileName+" && cat /tmp"+SSLHTMLFileName+" | ansi2html > /root/Documents/output/tls/"+SSLHTMLFileName+" && /root/shared/EzModeSSL -d . -o ../"+ClientName+"\""
							globals()['SSLContainer%s' % SSLCounter] = client.containers.run("delorean", SSLCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=NewSSLName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
							print("\nTestSSL command \"{}\" has been executed in container ".format(colored("testssl --warnings=batch --log --json --file ../../../data/tls_hosts.txt", "yellow"))+"{}".format(colored(NewSSLName, "yellow"))+". When complete outputs can be found within {}.".format(colored("output/tls/", "yellow")))						

					if re.search('wpscan', MasterInput[1], re.IGNORECASE):
						if os.stat(HTTPHostFileCheck).st_size != 0:
							with open(HTTPHostFileCheck, 'r') as file:
								HTTPHostRead = file.read()
								HTTPHostRead = HTTPHostRead.split("\n")
								if len(MasterInput) > 2: #Checking if user inputted a manual number of hosts per container.
									try:
										WpscanMaxHostNum = int(MasterInput[2])
									except:
										print("{}: Number of hosts must be an integer.".format(colored("ERROR", "red", attrs=["bold"])))
										continue
								else:
									WpscanMaxHostNum = 5 #Default number of hosts per container.
								HTTPHostRead = [x for x in HTTPHostRead if x] #Remove any empty entries
								if len(HTTPHostRead) > WpscanMaxHostNum:
									WpscanSubList = [HTTPHostRead[i:i + WpscanMaxHostNum] for i in range(0, len(HTTPHostRead), WpscanMaxHostNum)] #Breaking up list into sublists.
									for i in WpscanSubList:
										WpscanCounter = WpscanCounter+1
										WpscanNewName = 'Wpscan%s' % WpscanCounter
										WpscanFileName = WpscanNewName+"_output_"+now.strftime("%d%m%y_%H%M")+".txt"
										WpscanScopeFileName = AbsoluteDirectoryName+'/data/'+WpscanNewName+'_hosts.txt'
										with open(WpscanScopeFileName, 'w') as file:
											for line in i:
												file.write("%s\n" % line)
										WpscanHostNum = len(i)
										WpscanHostNum = str(WpscanHostNum)
										WpscanCommand = "/bin/bash -c \"mv /root/Documents/data/"+WpscanNewName+"_hosts.txt /tmp/ && python /root/shared/tools/wpscanloop.py -f /tmp/"+WpscanNewName+"_hosts.txt -o /root/Documents/output/http/"+WpscanFileName+"\""
										globals()['WpscanContainer%s' % WpscanCounter] = client.containers.run("delorean", WpscanCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=WpscanNewName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
										print("\nWPScan has been executed in container for "+WpscanHostNum+" hosts from the http scope file. When complete output can be found within {}.".format(colored("output/http/"+WpscanFileName, "yellow")))
								else:
									WpscanCounter = WpscanCounter+1
									WpscanNewName = 'Wpscan%s' % WpscanCounter
									WpscanFileName = WpscanNewName+"_output_"+now.strftime("%d%m%y_%H%M")+".txt"
									WpscanCommand = "/bin/bash -c \"python /root/shared/tools/wpscanloop.py -f /root/Documents/data/http_hosts.txt -o /root/Documents/output/http/"+WpscanFileName+"\""
									globals()['WpscanContainer%s' % WpscanCounter] = client.containers.run("delorean", WpscanCommand, detach=True, remove=True, cap_add=["NET_ADMIN"], network_mode="container:Emmett", privileged=False, name=WpscanNewName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
									print("\nWPScan has been executed in container for all hosts in http scope file. When complete output can be found within {}.".format(colored("output/http/"+WpscanFileName, "yellow")))
	


			if re.search('show', MasterInput[0], re.IGNORECASE): #Open Emmett management tools
				if len(MasterInput) == 1:
					print("""COMMAND HELP:
  Description - Show data regarding engagement and containers.
  Usage: show [option]
  OPTIONS:
     scope - Output engagement scope file.
     scope [scan type] - Output chosen engagement scope file.
     SCOPE TYPES:
       http
       main
       tls
     sessions - Open new terminal window showing active Emmett containers.
     status [container] - Show current terminal output of chosen container.
						""")
				else:
					if re.search('scope', MasterInput[1], re.IGNORECASE):#output the scope file
						if len(MasterInput) == 2:
							EngagementScope = AbsoluteDirectoryName+"/data/hosts.txt"
							HTTPScope = AbsoluteDirectoryName+"/data/http_hosts.txt"
							try:
								EngagementScope = open(EngagementScope, "r")
								EngagementScope = EngagementScope.read()
								HTTPScope = open(HTTPScope, "r")
								HTTPScope = HTTPScope.read()
								if EngagementScope == "":
									continue
								else:
									print("{}".format(colored("Main Scope:", attrs=["underline"])))
									print("{}".format(colored(EngagementScope, "yellow")))
								if HTTPScope == "":
									continue
								else:
									print("{}".format(colored("HTTP Scope:", attrs=["underline"])))
									print("{}".format(colored(HTTPScope, "yellow")))
							except:
								print("{}: Unable to open scope file.".format(colored("ERROR", "red", attrs=["bold"])))
						else:
							if re.search("main", MasterInput[2], re.IGNORECASE):
								EngagementScope = AbsoluteDirectoryName+"/data/hosts.txt"
							if re.search("tls", MasterInput[2], re.IGNORECASE):
								EngagementScope = AbsoluteDirectoryName+"/data/tls_hosts.txt"
							if re.search("http", MasterInput[2], re.IGNORECASE):
								EngagementScope = AbsoluteDirectoryName+"/data/http_hosts.txt"
							try:
								EngagementScope = open(EngagementScope, "r")
								EngagementScope = EngagementScope.read()
								print("{}".format(colored(EngagementScope, "yellow")))
							except:
								print("{}: Unable to open scope file.".format(colored("ERROR", "red", attrs=["bold"])))
					if re.search("sessions", MasterInput[1], re.IGNORECASE): #Opens emmettgui window
						ContainerList = client.containers.list(filters={"label":"Emmett"})
						print("Active Containers:")
						for x in ContainerList:
							x = x.name
							print("{}".format(colored(x, "yellow")))
					if re.search("status", MasterInput[1], re.IGNORECASE): #show status of container
						if len(MasterInput) == 2:
							print("""COMMAND HELP:
  Description - Show current terminal output of chosen container.
  Usage: show status [container]
								""")
						else:
							StatusContainerName = MasterInput[2].lower()
							StatusContainerName = StatusContainerName.capitalize()
							Status = subprocess.run("docker logs "+StatusContainerName, shell=True)


			if re.search('tail', MasterInput[0], re.IGNORECASE): #Tail output of running tool
				if len(MasterInput) == 1:
					print("""COMMAND HELP:
  Description - Show continous terminal output of chosen container.
  Usage: tail [container]
						""")
				else:
					TailContainerName = MasterInput[1].lower()
					TailContainerName = TailContainerName.capitalize()
					if os.name == "nt":
						Tail = subprocess.Popen(['start', 'cmd.exe', '/c', 'docker', 'logs', TailContainerName, '-f', '--tail', 'all'], shell=True)
					else:
						Tail = subprocess.Popen("xterm -e zsh -c \"docker logs "+TailContainerName+" -f --tail all\"", shell=True)

def client_selection():
	#Taking Client name and preparing for directory creation
	ClientNameInput= ''
	while True:
		ClientNameInput = input("Enter Client Name:") 

		if ClientNameInput:
			if re.match(assets.regex, ClientNameInput): #Checking user input for bad characters
				break
			else:
				print("{}: Your Input Contained Invalid Characters.".format(colored("ERROR", "red", attrs=["bold"])))
	ClientNameReplace = ClientNameInput.replace(" ", "_")
	ClientName = ClientNameReplace.lower()

	#Check If Engagement Exists
	ClientNameList = ClientNameInput.split()
	ClientNameCheck = ClientNameList[0]
	ClientNameFor = 0
	EngagementCheckList = []
	EngagementCheckListNum = 1

	for x in ClientNameList: #Checking Clients dir for sub-dirs including inputted client name
		Globcheck = glob.glob('../Clients/*'+ClientNameList[ClientNameFor]+'*')
		ClientNameFor = ClientNameFor+1
		
		for y in range(len(Globcheck)): #Appending discovered matches to list
			EngagementCheckList.append(Globcheck[y])
			
	if EngagementCheckList:
		EngagementCheckList = list(dict.fromkeys(EngagementCheckList)) #Removing duplicates from list

		for x in EngagementCheckList: #Outputting list to terminal
			EngagementCheckListNum = str(EngagementCheckListNum)
			try:
				x = x.split("/")
				x = x[2]
			except IndexError:
				x = x[1]
				x = x.split("\\")
				x = x[1]
			print(EngagementCheckListNum+" - "+x)
			EngagementCheckListNum = int(EngagementCheckListNum)+1

		#User selection if engagement exists already or is new
		EngagementInput = input("Choose From The List Of Previous Engagements Or Leave Blank To Return to Main Menu: ")
		try:	
			EngagementSelection = int(EngagementInput)-1
		except ValueError:
			return False
		global DirectoryName
		DirectoryName = EngagementCheckList[EngagementSelection]
		try:
			DirectoryName = DirectoryName.split("/")
			DirectoryName = DirectoryName[2]
		except IndexError:
			DirectoryName = DirectoryName[1]
			DirectoryName = DirectoryName.split("\\")
			DirectoryName = DirectoryName[1]
			if os.name == 'nt':
				GUI = subprocess.Popen("start cmd.exe /c python emmett.py --client "+ClientName+" --eng_dir "+DirectoryName, shell=True)
			else:
				GUI = subprocess.Popen("xterm -e zsh -c \"python3 emmett.py --client "+ClientName+" --eng_dir "+DirectoryName+"\"", shell=True)
			config_object = ConfigParser()
			config_object.read("./config.ini")
			config_object.set('GLOBAL', 'curreng', DirectoryName)
			with open('./config.ini', 'w') as configfile:
				config_object.write(configfile)
			return True
	else:
		print("{}".format(colored("No Existing Engagements Found For Client.", "red")))
		while True:
			EngagementInput = input("Would You Like To Create a New Engagement? (Y/N Default:N):")
			EngagementInput = EngagementInput.replace(" ", "")
			EngagementInput = EngagementInput.lower()
			if EngagementInput in ("y","n",""):
				break
		if EngagementInput == "y":
			new_engagement_creation(ClientName)
		else:
			return False

def new_engagement_creation(ClientName):
	#Take Engagement Dates
	StartDateList = []
	while True:
		StartDateInput = input("Enter Test Start Date dd/mm/yyyy (default, current date): ")
		try:
			if StartDateInput:
				StartDateListInt = StartDateInput.split("/")
				if len(StartDateListInt) == 3: #Checking if entered date is correct format
					StartDateListInt = [int(i) for i in StartDateListInt]
					for x in StartDateListInt:
						if x <= 9:
							x = "%02d" % (x,)
							StartDateList.append(x)
						else:
							StartDateList.append(x)
					StartDateList = [str(x) for x in StartDateList]
					StartDate = StartDateList[2]+"_"+StartDateList[1]+"_"+StartDateList[0]
					break
				else:
					print("{}: Invalid Date Format.".format(colored("ERROR", "red", attrs=["bold"])))
			else:
				StartDate = today.strftime("%Y_%m_%d")
				break
		except:
			print("{}: Invalid Entry.".format(colored("ERROR", "red", attrs=["bold"])))

#Create Engagement Directories and Scope File 
	global DirectoryName
	DirectoryName = StartDate+"_"+ClientName
	DirectoryLocation = "../Clients/"+DirectoryName
	EngagementConfigFileLocation = DirectoryLocation + "/data/emmett_config.ini"
	Path(DirectoryLocation).mkdir(parents=True, exist_ok=True)
	Path(DirectoryLocation+"/data").mkdir(parents=True, exist_ok=True)
	Path(DirectoryLocation+"/output/http").mkdir(parents=True, exist_ok=True)
	Path(DirectoryLocation+"/output/tls").mkdir(parents=True, exist_ok=True)
	Path(DirectoryLocation+"/output/tls/raw_outputs").mkdir(parents=True, exist_ok=True)
	Path(DirectoryLocation+"/output/nmap").mkdir(parents=True, exist_ok=True)
	Path(DirectoryLocation+"/output/nmap/raw_outputs").mkdir(parents=True, exist_ok=True) 
	Path(DirectoryLocation+"/screenshots").mkdir(parents=True, exist_ok=True)
	print("Engagement {} Successfully Created.".format(colored(DirectoryName, "yellow")))
	while True:
		EngagementTypeInput = input("What is the Engagement Type? (Web/Ext/API):")
		EngagementTypeInput = EngagementTypeInput.replace(" ","")
		EngagementTypeInput = EngagementTypeInput.lower()
		if EngagementTypeInput in ("web","ext","api"):
			break
	if EngagementTypeInput in ("web", "api"):
		while True: #If web or api test selected check if they want Burp to boot automatically
			BurpBootInput = input("Would you like to execute Burpsuite automatically when opening this engagement? (Y/N Default:N): ")
			BurpBootInput = BurpBootInput.replace(" ", "")
			BurpBootInput = BurpBootInput.lower()
			if BurpBootInput in ("y","n",""):
				break
		if BurpBootInput == "y":
			print("Burpsuite will be automatically executed when opening this engagement. This can be changed at anytime from within Emmetts CLI using the \"{}\" command.".format(colored("engagement edit", "yellow")))
			BurpBoot = "on"
		else:
			BurpBoot = "off"
	else:
		BurpBoot = "off"
	curreng_object["ENGINFO"] = {
	"client": ClientName,
	"type": EngagementTypeInput,
	"burp": BurpBoot,
	"autoeng_toggle": "off"
	}
	curreng_object["AUTOENG"] = {
	"state": "Not Started",
	"engagementnmaptcp": "Not Started",
	"engagementnmapudp": "Not Started",
	"engagementtestssl": "Awaiting TCP Scan Results.",
	"engagementlivehosts": "Not Started",
	"nmaptcp_file": "None"
	}
	with open(EngagementConfigFileLocation, 'w') as conf:
		curreng_object.write(conf)
	print("Enter/Paste Your Testing Scope. {} (Windows) or ".format(colored("Ctrl-Z", "yellow"))+"{} (Linux) on a New Line to Save.".format(colored("Ctrl-D", "yellow")))
	HostFileLocation = DirectoryLocation + "/data/hosts.txt"
	HTTPHostFileLocation = DirectoryLocation + "/data/http_hosts.txt"
	TLSHostFileLocation = DirectoryLocation + "/data/tls_hosts.txt"
	HostFile = open(HostFileLocation, 'w')
	HTTPHostFile = open(HTTPHostFileLocation, 'w')
	TLSHostFile = open(TLSHostFileLocation, 'a').close()
	EngagementScope = []
	HTTPEngagementScope = []
	while True:
	    try:
	        line = input()
	        if line:
	        	if re.match(assets.scope_regex, line): #Checking user input for bad characters
	        		if re.match(assets.url_regex, line): #Checking if user input is a URL
	        			if line not in HTTPEngagementScope:
		        			HTTPEngagementScope.append(line)
		        			HTTPDomain = line.split('/')
		        			HTTPDomain = HTTPDomain[2]
		        			if HTTPDomain not in EngagementScope:
			        			EngagementScope.append(HTTPDomain)
	        		else:
	        			if line not in EngagementScope:
			        		EngagementScope.append(line)
	        	else:
	        		print("{}: The Previous Line Contained Inavlid Characters And Will Be Omitted From The Scope File. Please Add Manually Afterwards If Required.".format(colored("ERROR", "red", attrs=["bold"])))
	    except EOFError:
	        break

	for x in range(len(EngagementScope)):
	    HostFile.write(EngagementScope[x]+"\n")
	for x in range(len(HTTPEngagementScope)):
		HTTPHostFile.write(HTTPEngagementScope[x]+"\n")

	HTTPHostFile.close()
	HostFile.close()
	print("{}".format(colored("Scope File Successfully Created", "green")))
	print("{}".format(colored("Engagement Successfully Created", "green")))
	while True:
		NewEngagementInput = input("Would You Like To Connect To This Engagement Now? (Y/N Default:Y):")
		NewEngagementInput = NewEngagementInput.replace(" ", "")
		NewEngagementInput = NewEngagementInput.lower()
		if NewEngagementInput in ("y","n",""):
			break
	if NewEngagementInput == "n":
		return False
	else:
		if os.name == 'nt':
			GUI = subprocess.Popen("start cmd.exe /c python emmett.py --client "+ClientName+" --eng_dir "+DirectoryName, shell=True)
		else:
			GUI = subprocess.Popen("xterm -e zsh -c \"python3 emmett.py --client "+ClientName+" --eng_dir "+DirectoryName+"\"", shell=True)
		config_object = ConfigParser()
		config_object.read("./config.ini")
		config_object.set('GLOBAL', 'curreng', DirectoryName)
		with open('./config.ini', 'w') as configfile:
			config_object.write(configfile)
		return True
def vpn_only_mode():
	try:
		AbsoluteBuildName = Path.cwd() / "build/"
		AbsoluteBuildName = str(AbsoluteBuildName)
		AbsoluteEmmettBuildName = AbsoluteBuildName + "/Emmett/shared"
		EmmettBuildVolume = AbsoluteEmmettBuildName+":/root/shared/"
		EmmettContainer = client.containers.run("emmett", detach=True, remove=True, devices=["/dev/net/tun"], cap_add=["NET_ADMIN"], privileged=False, name="Emmett", labels=["Emmett"], ports={'8118':'8118'}, volumes=[EmmettBuildVolume])
	except docker.errors.APIError:
		return False

def sessions_exit():
	config_object = ConfigParser()
	config_object.read("./config.ini")
	config_object.set('GLOBAL', 'curreng', 'None')
	with open('./config.ini', 'w') as configfile:
		config_object.write(configfile)
	ContainerList = client.containers.list(filters={"label":"Emmett"})
	for x in ContainerList: #Breaking up ContainerList entries to be just container IDs and killing the associated containers
		x = str(x)
		x = x.replace("<Container: ", "")
		x = x.replace(">", "")
		subprocess.run(['docker', 'container', 'kill', x], stdout=subprocess.DEVNULL)
	ContainerList = client.containers.list(filters={"label":"Emmett"})
	if not ContainerList:
		ContainerProgress = "{}".format(colored("All Containers Successfully Removed.", "green"))
	else:
		ContainerProgress = "{}".format(colored("Problem Closing All Containers, Manual Interaction Required.", "red"))
	return ContainerProgress

if __name__ == "__main__":
	#Update Image
	if args.update == True:
		assets.image_update()
		assets.burpsuite_update()
		exit()

	if args.vpn_only == True:
		vpn_only_mode()

	if args.setup == False and args.no_pull == True:
		print(assets.logo)
		print("The --no-pull procedure is part of the setup process and requires the use of --setup also.")
		exit()
	if args.setup == False and args.no_image == True:
		print(assets.logo)
		print("The --no-image procedure is part of the setup process and requires the use of --setup also.")
		exit()
	if args.setup == False and args.no_docker == True:
		print(assets.logo)
		print("The --no-docker procedure is part of the setup process and requires the use of --setup also.")
		exit()
	if args.setup == False and args.no_startup == True:
		print(assets.logo)
		print("The --no-startup procedure is part of the setup process and requires the use of --setup also.")
		exit()

	if args.setup == True:
		if args.no_pull == False and args.no_docker == False:
			assets.kali_pull()
		if args.no_image == False and args.no_docker == False:
			assets.image_create()
		#Startup Script Setup
		if args.no_burp == False:
			assets.burpsuite_update()
		if args.no_startup == False:
			assets.startupscript_generate()
		if args.no_bat == False:
			assets.batfile_generate()
		exit()

	if args.uninstall == True:
		assets.uninstall()
		exit()

	if args.client and args.eng_dir:
		print("{}".format(colored(assets.logo, "green"))+assets.slogan)
		main(args.client, args.eng_dir)