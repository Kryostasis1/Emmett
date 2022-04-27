import docker
import glob
from datetime import date
from pathlib import Path
client = docker.from_env()
today = date.today()

#Emmett Logo
print()
print()
print("___________                       __    __   ")
print("\\_   _____/ _____   _____   _____/  |__/  |_ ")
print(" |    __)_ /     \\ /     \\_/ __ \\   __\\   __\\")
print(" |        \\  Y Y  \\  Y Y  \\  ___/|  |  |  |  ")
print("/_______  /__|_|  /__|_|  /\\___  >__|  |__|  ")
print("        \\/      \\/      \\/     \\/            ")
print("The Way I See It, If You're Gonna Build An Engagement, Why Not Do It With Some Style?")
print()
print()
print()

#Checking For Previous Engagement
PrevEng = open("Config.txt", "r")
PrevEng = PrevEng.read()
print("Previous Engagement - "+PrevEng)
print()
ClientNameInput = input("Would You Like To Continue This Engagement (Y/N)? ")
ClientNameInput = ClientNameInput.replace(" ", "")
ClientNameInput = ClientNameInput.lower()
if ClientNameInput == "y":
	print()
	print("Reaching 88mph...")
	DirectoryName = PrevEng
	#Initiate Docker
	AbsoluteDirectoryName = "..\\Clients\\"+DirectoryName
	AbsoluteDirectoryName = Path.cwd() / AbsoluteDirectoryName
	AbsoluteDirectoryName = str(AbsoluteDirectoryName)
	AbsoluteBuildName = Path.cwd() / "build\\ecscproxy"
	AbsoluteBuildName = str(AbsoluteBuildName)
	DocumentsVolume = AbsoluteDirectoryName+":/root/Documents"
	BuildVolume = AbsoluteBuildName+":/root/shared/"
	client.containers.run("emmett", detach=True, remove=False, devices="/dev/net/tun", privileged=True, name="DeLorean", ports={'8118':'8118','22':'11111'}, volumes=[DocumentsVolume, BuildVolume])
	print()
	print("Awaiting Lightning Strike...")
	print()
	quit()

#Taking Client name and preparing for directory creation
ClientNameInput= ''
while True:
	ClientNameInput = input("Enter Client Name:") 

	if ClientNameInput:
		break
ClientNameReplace = ClientNameInput.replace(" ", "_")
ClientName = ClientNameReplace.lower()

#Check If Engagement Exists
ClientNameList = ClientNameInput.split()
ClientNameCheck = ClientNameList[0]
ClientNameFor = 0
EngagementCheckList = []
EngagementCheckListNum = 1

for x in ClientNameList: #Checking Clients dir for sub-dirs including inputted client name
	Globcheck = glob.glob('..\\Clients\\*'+ClientNameList[ClientNameFor]+'*')
	ClientNameFor = ClientNameFor+1
	
	for y in range(len(Globcheck)): #Appending discovered matches to list
		EngagementCheckList.append(Globcheck[y])

EngagementCheckList = list(dict.fromkeys(EngagementCheckList)) #Removing duplicates from list

for x in EngagementCheckList: #Outputting list to terminal
	EngagementCheckListNum = str(EngagementCheckListNum)
	x = x.split("\\")
	x = x[2]
	print(EngagementCheckListNum+" - "+x)
	EngagementCheckListNum = int(EngagementCheckListNum)+1

#User selection if engagement exists already or is new
EngagementInput = input("Choose From The List Of Previous Engagements Or Leave Blank For A New Engagement: ")
try:	
	EngagementSelection = int(EngagementInput)-1
except ValueError:
	EngagementSelection = None

#Performing actions based on previous selection
if EngagementSelection == None:
	#Take Engagement Dates
	StartDateInput = input("Enter Test Start Date dd/mm/yyyy (default current days date): ")
	if StartDateInput:
		StartDateList = StartDateInput.split("/")
		StartDate = StartDateList[2]+"_"+StartDateList[1]+"_"+StartDateList[0]
	else:
		StartDate = today.strftime("%Y_%m_%d")

	#Create Engagement Directory
	DirectoryName = StartDate+"_"+ClientName
	DirectoryLocation = "..\\Clients\\"+DirectoryName
	Path("..\\Clients\\"+DirectoryName).mkdir(parents=True, exist_ok=True)
	print("Engagement "+DirectoryName+" Successfully Created")
else:
	DirectoryName = EngagementCheckList[EngagementSelection]
	DirectoryName = DirectoryName.split("\\")
	DirectoryName = DirectoryName[2]

#Initiate Docker
AbsoluteDirectoryName = "..\\Clients\\"+DirectoryName
AbsoluteDirectoryName = Path.cwd() / AbsoluteDirectoryName
AbsoluteDirectoryName = str(AbsoluteDirectoryName)
AbsoluteBuildName = Path.cwd() / "build\\ecscproxy"
AbsoluteBuildName = str(AbsoluteBuildName)
DocumentsVolume = AbsoluteDirectoryName+":/root/Documents"
BuildVolume = AbsoluteBuildName+":/root/shared/"
client.containers.run("emmett", remove=True, detach=True, devices="/dev/net/tun", privileged=True, name="DeLorean", ports={'8118':'8118','22':'11111'}, volumes=[DocumentsVolume, BuildVolume])
print()
print("Docker Initiated.")
print()
print("Connecting...")

#Save Previous Engagement
PrevEng = open("Config.txt", "w")
PrevEng.write(DirectoryName)
PrevEng.close()