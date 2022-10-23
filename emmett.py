import docker
import glob
import re
import subprocess
import os
import argparse
from datetime import date
from pathlib import Path
from prompt_toolkit import print_formatted_text, HTML, PromptSession, Application
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

## OUR LIBRARY
from lib import assets
from lib import modules

client = docker.from_env()
today = date.today()

#Header
usage_text = 'python emmett.py'
example_text = '''Example:
python emmett.py (Standard run)
python emmett.py --setup (Perform full setup)
python emmett.py --setup --no-docker (Perform setup without any Docker actions)
python setup.py -u (Update current Emmett images)'''
parser = argparse.ArgumentParser(usage=usage_text, epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)

#Arguments
parser.add_argument("-u", "--update", help="Update existing Emmett image OS.\n", action="store_true")
parser.add_argument("--setup", help="Perform initial setup.\n", action="store_true")
parser.add_argument("--no-pull", help="Do not pull new kali image.\n", action="store_true")
parser.add_argument("--no-image", help="Do not create an Emmett image.\n", action="store_true")
parser.add_argument("--no-docker", help="Do not perform any Docker actions (same as running --no-image and --no-pull).\n", action="store_true") 
parser.add_argument("--no-startup", help="Do not create startup script.\n", action="store_true")
parser.add_argument("--uninstall", help="Uninstall Emmett Assets.\n", action="store_true")

args = parser.parse_args()

#Setup
#Update Image
if args.update == True:
	assets.image_update()
	exit()

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
	if args.no_startup == False:
		assets.startupscript_generate()
	exit()

if args.uninstall == True:
	assets.uninstall()
	exit()

"""
def ContainerSearch(): #Searching for active containers labelled Emmett
	ContainerList = client.containers.list(filters={"label":"Emmett"})
	print("""
# Active Containers: 
""")
	for x in ContainerList:
		ContainerName = x.name
		ContainerStatus = x.status
		if ContainerStatus == "running":
			print_formatted_text(HTML('<ansigreen>'+ContainerName+" - "+ContainerStatus+'</ansigreen>'))
		else:
			print_formatted_text(HTML('<ansired>'+ContainerName+" - "+ContainerStatus+'</ansired>'))
"""
def main():
	#Initiate Docker
	AbsoluteDirectoryName = "../Clients/"+DirectoryName
	AbsoluteDirectoryName = Path.cwd() / AbsoluteDirectoryName
	AbsoluteDirectoryName = str(AbsoluteDirectoryName)
	#Getting shared folder locations and intialising VPN and initial Kali containers
	AbsoluteBuildName = Path.cwd() / "build/"
	AbsoluteBuildName = str(AbsoluteBuildName)
	AbsoluteEmmettBuildName = AbsoluteBuildName + "/Emmett/shared"
	AbsoluteDeLoreanBuildName = AbsoluteBuildName + "/DeLoreans/shared"
	DocumentsVolume = AbsoluteDirectoryName+":/root/Documents"
	EmmettBuildVolume = AbsoluteEmmettBuildName+":/root/shared/"
	DeLoreansBuildVolume = AbsoluteDeLoreanBuildName+":/root/shared/"
	KaliCounter = 1
	NmapCounter = 0
	SSLCounter = 0
	InitialKaliName = 'Kali%s' % KaliCounter
	try:
		EmmettContainer = client.containers.run("emmett", detach=True, remove=True, devices=["/dev/net/tun"], cap_add=["NET_ADMIN"], privileged=False, name="Emmett", labels=["Emmett"], ports={'8118':'8118'}, volumes=[EmmettBuildVolume])
	except docker.errors.APIError:
		pass
	try:
		globals()['KaliContainer%s' % KaliCounter] = client.containers.run("delorean", detach=True, remove=True, network_mode="container:Emmett", privileged=False, name=InitialKaliName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
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

	#CLI Prompt
	cliSession = PromptSession()
	cliCompleter = NestedCompleter.from_nested_dict({ #Autocomplete setup
		'help': None,
		'connect': None,
		'kill': {
			'all': None
		},
		'run': {
			'engagement': None,
			'nmap': None,
			'testssl': None
		},
		'status': None,
		'tail': None,
		'exit': None,
		'new': {
			'emmett': None,
			'kali': None
		},
		'scope': {
			'create': None,
			'add': None,
			'show': None
		},
	})
	if os.name == 'nt':
		GUI = subprocess.Popen("start cmd.exe /c python lib\\emmettgui.py", shell=True)
	else:
		GUI = subprocess.Popen("xterm -e zsh -c \"python3 lib/emmettgui.py\"", shell=True)
	MasterInput = ""
	while True: #Prompt Loop
		ContainerList = client.containers.list(filters={"label":"Emmett"})
		"""if MasterInput == "": #Active Containers List
			ContainerSearch() """
		MasterInput = cliSession.prompt("> ", completer=cliCompleter, auto_suggest=AutoSuggestFromHistory())
		MasterInput = MasterInput.split()
		if not MasterInput:
			MasterInput = ""
		else: #Start of Commands List
			if MasterInput[0] == "help" or MasterInput[0] == "h"or MasterInput[0] == "?": #Help output
				print("""COMMAND LIST:
  connect - Open a bash session on container.
  	 Usage: connect [container]

  exit - Kill all Emmett jobs and exit.
  help - Show this screen.
  kill - Kill containers
	 Usage:  kill [container] - Kill selected Emmett container.
		kill all - Kill all Emmett containers.

  new - Start new Emmett container.
	Usage:  new [container]
	CONTAINER TYPES:
	  Emmett - VPN proxy container (this is unique, only 1 can run at a time).
	  Kali - Starts new persistent Kali container.

  run - Execute a tool against scope file. Outputs will be given in the engagements output folder.
	Usage: run [tool]
	TOOL LIST:
	  engagement - Runs all tools.
	  nmap
	  testssl	

  scope - Interact with engagement scope file.
  	Usage: scope [options]
  	OPTIONS:
	  show - Output engagement scope file.
  	  create - Create engagement scope file.
  	  add - Add to engagement scope file.

  status - Show current terminal output of chosen container.
	   Usage: status [container]
  tail - Show continous terminal output of chosen container.
  	   Usage: tail [container]	
				""")
			if MasterInput[0] == "kill": #Command for killing containers
				if len(MasterInput) == 1:
					print("""COMMAND HELP:
  Description - Kill containers
  Usage:  kill [container] - Kill selected Emmett container.
	  kill all - Kill all Emmett containers.
						""")
				else:
					if MasterInput[1] == "all":
						print("Stopping All Containers.")
						for x in ContainerList: #Breaking up ContainerList entries to be just container IDs and killing the associated containers
							x = str(x)
							x = x.replace("<Container: ", "")
							x = x.replace(">", "")
							subprocess.run(['docker', 'container', 'kill', x], stdout=subprocess.DEVNULL)			
					else:
						ContainerKill = MasterInput[1]
						ContainerKill = ContainerKill.capitalize()
						subprocess.run(['docker', 'container', 'kill', ContainerKill], stdout=subprocess.DEVNULL)
						# ContainerSearch()

			if MasterInput[0] == "new": #Command for starting new Dockers
				if len(MasterInput) == 1:
					print("""COMMAND HELP:
  Description - Start new Emmett container.
  Usage:  new [container]
  CONTAINER TYPES:
    Emmett - VPN proxy container (this is unique, only 1 can run at a time).
    Kali - Starts new persistent Kali container.
						""")
				else:
					if re.search('emmett', MasterInput[1], re.IGNORECASE):
						EmmettContainer = client.containers.run("emmett", detach=True, remove=True, devices=["/dev/net/tun"], cap_add=["NET_ADMIN"], privileged=False, name="Emmett", labels=["Emmett"], ports={'8118':'8118'}, volumes=[EmmettBuildVolume])
						# ContainerSearch()
					if MasterInput[1] == "kali":
						KaliCounter = KaliCounter+1
						NewKaliName = 'Kali%s' % KaliCounter
						globals()['KaliContainer%s' % KaliCounter] = client.containers.run("delorean", detach=True, remove=True, network_mode="container:Emmett", privileged=False, name=NewKaliName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
						# ContainerSearch()

			if MasterInput[0] == "connect": #Connect to an Emmett container with a bash session
				if len(MasterInput) == 1:
					print("""COMMAND HELP:
  Description - Open a bash session on container.
  Usage: connect [container]
						""")
				else:
					print("Attempting to Connect You to "+MasterInput[1])
					ConnectContainerName = MasterInput[1].capitalize()
					try: 
						if os.name == "nt":
							subprocess.run("start cmd.exe /c docker exec -it "+ConnectContainerName+" bash -i", shell=True)
						else:
							print("Copy/Paste \"docker exec -it "+ConnectContainerName+" bash -i\" Into a New Terminal Window.")
					except:
						print("Unable to Connect to "+MasterInput[1])


			### MODULE USAGE WILL BE HERE, 
			### NOTE: STARTING TO SLOWLY REFACTOR SO WILL LOOK MESSY FOR A BIT

			if MasterInput[0] == "run": #Run a tool
				if len(MasterInput) == 1:
					help_text_to_print = """COMMAND HELP:
  Description - Execute a tool against scope file. Outputs will be given in the engagements output folder.
  Usage: run [tool]
  Commands:
    engagement - Runs all tools.

  Modules:\n"""
					all_module_data = modules.get_all_module_info()
					for m in all_module_data:
						help_text_to_print += "\t" + m + " - " + all_module_data[m]["description"] + "\n"

					print(help_text_to_print)
				else:
					run_command_input = MasterInput[1]
					if re.search('engagement', run_command_input, re.IGNORECASE):
						NmapCounter = NmapCounter+1
						NewNmapName = 'Nmap%s' % NmapCounter
						globals()['NmapContainer%s' % NmapCounter] = client.containers.run("delorean", "nmap -sV -p- -iL /root/Documents/hosts -v -oN /root/Documents/output/nmap/tcp_output", detach=True, remove=True, network_mode="container:Emmett", privileged=False, name=NewNmapName, labels=["Emmett"], volumes=[DocumentsVolume])
						SSLCounter = SSLCounter+1
						NewSSLName = 'Testssl%s' % SSLCounter
						SSLCommand = "/bin/bash -c \"cd /root/Documents/output/tls && testssl --warnings=batch --html --json --file ../../hosts && /root/shared/EzModeSSL -d . -o "+ClientName+"\""
						globals()['SSLContainer%s' % SSLCounter] = client.containers.run("delorean", SSLCommand, detach=True, remove=True, network_mode="container:Emmett", privileged=False, name=NewSSLName, labels=["Emmett"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
					else:
						### SWITCHING TO MODULE BASED SO REMOVED HARDCODED STATEMENTS
						if modules.is_module(run_command_input):
							optional_args = modules.OPTIONAL_ARGS.copy()
							optional_args["<--CLIENT_NAME-->"] = "Test"

							## TODO: we want to pass in an object here that has all our information for find/replace in commands that need it
							# perhaps a class object that is populate once per client target? Includes some base data?
							module_command = modules.get_module_cmd(run_command_input, optional_args)
							globals()['NmapContainer%s' % NmapCounter] = client.containers.run(
								"delorean", 
								module_command,
								detach=True, 
								remove=True, 
								network_mode="container:Emmett", 
								privileged=False, 
								name=run_command_input + str(modules.get_module_info(run_command_input, "runCount")), 
								labels=["Emmett"], 
								volumes=[DocumentsVolume, DeLoreansBuildVolume]
							)
							modules.run_module_requested(run_command_input)
						else:
							print("Sorry, not a recognised module")

			if MasterInput[0] == "scope": #Actions relating to the scope
				if len(MasterInput) == 1:
					EngagementScope = AbsoluteDirectoryName+"/hosts"
					EngagementScope = open(EngagementScope, "r")
					EngagementScope = EngagementScope.read()
					print(EngagementScope)
				else:
					if re.search('show', MasterInput[1], re.IGNORECASE):
						EngagementScope = AbsoluteDirectoryName+"/hosts"
						EngagementScope = open(EngagementScope, "r")
						EngagementScope = EngagementScope.read()
						print(EngagementScope)

					if re.search('create', MasterInput[1], re.IGNORECASE):
						DirectoryLocation = "../Clients/"+DirectoryName
						print("""WARNING: THIS WILL OVERWRITE ANY EXISTING SCOPE FOR THIS ENGAGEMENT!

Enter/Paste Your Testing Scope. Ctrl-Z (Windows) or Ctrl-D (Linux) on a New Line to Save.""")
						HostFileLocation = DirectoryLocation + "/hosts"
						HostFile = open(HostFileLocation, 'w')
						EngagementScope = []
						while True:
						    try:
						        line = input()
						        if line:
						        	if re.match(assets.scope_regex, line): #Checking user input for bad characters
						        		EngagementScope.append(line)
						        	else:
						        		print("The Previous Line Contained Inavlid Characters And Will Be Omitted From The Scope File. Please Add Manually Afterwards If Required.")
						    except EOFError:
						        break

						for x in range(len(EngagementScope)):
						    HostFile.write(EngagementScope[x]+"\n")

						HostFile.close()
						print("Scope File Successfully Created")

					if re.search('add', MasterInput[1], re.IGNORECASE):
						DirectoryLocation = "../Clients/"+DirectoryName
						print("Enter/Paste Your Testing Scope. Ctrl-Z (Windows) or Ctrl-D (Linux) on a New Line to Save.")
						HostFileLocation = DirectoryLocation + "/hosts"
						HostFile = open(HostFileLocation, 'a')
						EngagementScope = []
						while True:
						    try:
						        line = input()
						        if line:
						        	if re.match(assets.scope_regex, line): #Checking user input for bad characters
						        		EngagementScope.append(line)
						        	else:
						        		print("The Previous Line Contained Inavlid Characters And Will Be Omitted From The Scope File. Please Add Manually Afterwards If Required.")
						    except EOFError:
						        break

						for x in range(len(EngagementScope)):
						    HostFile.write(EngagementScope[x]+"\n")

						HostFile.close()
						print("Scope File Successfully Updated.")

			if MasterInput[0] == "status": #Check status of running tool
				StatusContainerName = MasterInput[1].lower()
				StatusContainerName = StatusContainerName.capitalize()
				Status = subprocess.run("docker logs "+StatusContainerName, shell=True)

			if MasterInput[0] == "tail": #Tail output of running tool
				TailContainerName = MasterInput[1].lower()
				TailContainerName = TailContainerName.capitalize()
				if os.name == "nt":
					Tail = subprocess.Popen(['start', 'cmd.exe', '/c', 'docker', 'logs', TailContainerName, '-f', '--tail', 'all'], shell=True)
				else:
					Tail = subprocess.Popen("xterm -e zsh -c \"docker logs "+TailContainerName+" -f --tail all\"", shell=True)

			if MasterInput[0] == "exit": #Command for exiting Emmett CLI
				print("Stopping All Containers.")
				for x in ContainerList: #Breaking up ContainerList entries to be just container IDs and killing the associated containers
					x = str(x)
					x = x.replace("<Container: ", "")
					x = x.replace(">", "")
					subprocess.run(['docker', 'container', 'kill', x], stdout=subprocess.DEVNULL)
				#Save Previous Engagement
				PrevEng = open("config.txt", "w")
				PrevEng.write(DirectoryName)
				PrevEng.close()		
				exit()

#Emmett Logo
print(assets.logo)

#Checking For Previous Engagement
PrevEng = open("config.txt", "r")
PrevEng = PrevEng.read()
print("Previous Engagement - "+PrevEng)
print()
while True: #Check user input for y/n
	ClientNameInput = input("Would You Like To Continue This Engagement (Y/N)? ")
	ClientNameInput = ClientNameInput.replace(" ", "")
	ClientNameInput = ClientNameInput.lower()
	if ClientNameInput in ("y","n"):
		break
if ClientNameInput == "y":
	print()
	print("Reaching 88mph...")
	PrevEngList = PrevEng.split("_")
	ClientName = PrevEngList[3]
	DirectoryName = PrevEng
	main()

#Taking Client name and preparing for directory creation
ClientNameInput= ''
while True:
	ClientNameInput = input("Enter Client Name:") 

	if ClientNameInput:
		if re.match(assets.regex, ClientNameInput): #Checking user input for bad characters
			break
		else:
			print("Your Input Contained Invalid Characters.")
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
	EngagementInput = input("Choose From The List Of Previous Engagements Or Leave Blank For A New Engagement: ")
	try:	
		EngagementSelection = int(EngagementInput)-1
	except ValueError:
		EngagementSelection = None
		print("Creating New Engagement.")
else:
	print("""No Existing Engagements Found For Client.
Creating New Engagement.""")
	EngagementSelection = None

#Performing actions based on previous selection
if EngagementSelection == None:
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
					print("Invalid Date Format.")
			else:
				StartDate = today.strftime("%Y_%m_%d")
				break
		except:
			print("Invalid Entry.")

	#Create Engagement Directories and Scope File
	DirectoryName = StartDate+"_"+ClientName
	DirectoryLocation = "../Clients/"+DirectoryName
	Path(DirectoryLocation).mkdir(parents=True, exist_ok=True)
	Path(DirectoryLocation+"/output/tls").mkdir(parents=True, exist_ok=True)
	Path(DirectoryLocation+"/output/nmap").mkdir(parents=True, exist_ok=True) 
	Path(DirectoryLocation+"/screenshots").mkdir(parents=True, exist_ok=True)
	print("Engagement "+DirectoryName+" Successfully Created")
	print()
	print("Enter/Paste Your Testing Scope. Ctrl-Z (Windows) or Ctrl-D (Linux) on a New Line to Save.")
	HostFileLocation = DirectoryLocation + "/hosts"
	HostFile = open(HostFileLocation, 'w')
	EngagementScope = []
	while True:
	    try:
	        line = input()
	        if line:
	        	if re.match(assets.scope_regex, line): #Checking user input for bad characters
	        		EngagementScope.append(line)
	        	else:
	        		print("The Previous Line Contained Inavlid Characters And Will Be Omitted From The Scope File. Please Add Manually Afterwards If Required.")
	    except EOFError:
	        break

	for x in range(len(EngagementScope)):
	    HostFile.write(EngagementScope[x]+"\n")

	HostFile.close()
	print("Scope File Successfully Created")
	main()
else:
	DirectoryName = EngagementCheckList[EngagementSelection]
	try:
		DirectoryName = DirectoryName.split("/")
		DirectoryName = DirectoryName[2]
	except IndexError:
			DirectoryName = DirectoryName[1]
			DirectoryName = DirectoryName.split("\\")
			DirectoryName = DirectoryName[1]
	main()

