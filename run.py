from prompt_toolkit.widgets import SearchToolbar, TextArea
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings, ConditionalKeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.filters import Condition
from configparser import ConfigParser
from prompt_toolkit.layout.containers import Float, FloatContainer, Window
from prompt_toolkit.widgets import Frame
from lib import assets
from termcolor import colored
import docker
import emmett
import subprocess
import os
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
client = docker.from_env()
now = datetime.now()
config_object = ConfigParser()
config_object.read("./config.ini")
global_config = config_object['GLOBAL']
DeloreanBuildPath = Path.cwd() / "build/DeLoreans/shared"
DeloreanBuildPath = str(DeloreanBuildPath)
config_object.set('GLOBAL', 'deloreanpath', DeloreanBuildPath)
with open('./config.ini', 'w') as configfile:
    config_object.write(configfile)
global ClientName
global DirectoryName
ClientName = "None"
DirectoryName = "None"
exit_option = 0
output = 0
setup_option = 0
update_output = 0
menuselect_main = True
menuselect_update = False
menuselect_exit = False
menuselect_setup = False

if global_config['setup'] == "False": #Check if Emmett isnt setup yet
    menuselect_main = False
    menuselect_setup = True

def engagement_scope(): #Engagement Scope
    if global_config['curreng'] != "None":
        curreng_object = ConfigParser()
        CurrEngFolder = "../Clients/"+global_config['curreng']
        CurrEngConfigLocation = CurrEngFolder+"/data/emmett_config.ini"
        curreng_object.read(CurrEngConfigLocation)
        Eng_Config = curreng_object['ENGINFO']
        if Eng_Config['type'] == 'ext':
            ScopeFile = CurrEngFolder+"/data/hosts.txt"
            with open(ScopeFile, 'r') as file:
                scope = [("underline", "Scope\n")]

                for line in file:
                    line = line.strip()
                    line = line+"\n"
                    scope.append(("class:right", line))
        else:
            MainScopeFile = CurrEngFolder+"/data/hosts.txt"
            MainScopeFileCheck = Path(MainScopeFile)
            HTTPScopeFile = CurrEngFolder+"/data/http_hosts.txt"
            HTTPScopeFileCheck = Path(HTTPScopeFile)
            scope = []
            with open(MainScopeFile, 'r') as file:
                if os.stat(MainScopeFileCheck).st_size != 0:
                    scope.append(("underline", "Main Scope\n"))

                    for line in file:
                        line = line.strip("\n")
                        line = line+"\n"
                        scope.append(("class:right", line))

            try:
                with open(HTTPScopeFile, 'r') as file:
                    if os.stat(HTTPScopeFileCheck).st_size != 0:
                        scope.append(("underline", "\nHTTP Scope\n"))

                        for line in file:
                            line = line.strip()
                            line = line+"\n"
                            scope.append(("class:right", line))
            except FileNotFoundError:
                open(HTTPScopeFile, 'a').close()
        return scope

def get_titlebar(): #Top title logo area
    titlebar = [
            ("fg:green", assets.app_logo),
            ("class:title", assets.app_slogan),
        ]
    return titlebar

def get_sessionbar(): #Top title logo area for container sessions screen
    titlebar = [
            ("fg:green", assets.app_logo),
            ("class:title", assets.app_slogan),
            ("class:title", " (Press [Ctrl-B] to return to main menu or [Ctrl-Q] to exit Emmett.)\n")
        ]
    if global_config['curreng'] != "None":
        titlebar.append(("class:title", " ([Ctrl-S] to hide/show AutoEngagement progress.)"))
    return titlebar

def main_menu(): #Main Menu and Update Menu
    config_object.read("./config.ini")
    global_config = config_object['GLOBAL']
    if menuselect_setup == True:
        menu_area = [#Setup menu UI
                ("class:left", "Current Menu: "),
                ("fg:yellow", "Setup\n\n"),
                ("class:left", "New installation detected, run initial setup?\n"),
                ("class:left", "    1) Yes\n"),
                ("class:left", "    2) No")
        ]
    if menuselect_main == True:
        PrevEng = global_config["preveng"]
        menu_area = [#Main menu UI
                ("class:left", "Current Menu: "),
                ("fg:yellow", "Main Menu\n"),
                ("class:left", "Previous Engagement: "),
                ("fg:yellow", PrevEng+"\n\n"),
                ("class:left"," Select from the menu:\n\n"),
                ("class:left", "    1) Continue Previous Engagement\n"),
                ("class:left", "    2) Search for Existing Engagement\n"),
                ("class:left", "    3) Create a New Engagement\n"),
                ("class:left", "    4) VPN Only Mode\n"),
                ("class:left", "    5) Open Sessions Window\n"),
                ("class:left", "    6) Update Emmett\n"),
                ("class:left", "    7) Exit\n")
            ]

    if menuselect_update == True: #Update menu

        menu_area = [ #Update Menu Selection UI
                ("class:left", "Current Menu: "),
                ("fg:yellow", "Update Emmett\n\n"),
                ("class:left"," Select from the menu:\n\n"),
                ("class:left", "    1) Update Kali\n"),
                ("class:left", "    2) Update Burpsuite\n"),
                ("class:left", "    3) Update Both\n"),
                ("class:left", "    4) Back to Main Menu\n")
            ]
    if menuselect_exit == True: #Exit Menu
        menu_area = [ #Update Menu Selection UI for Exit
                ("class:left", "Would You Like to Exit All Running Emmett Container Sessions?\n"),
                ("class:left", "    1) Yes\n"),
                ("class:left", "    2) No\n"),
                ("class:left", "    3) Back to Main Menu\n\n"),
                ("fg:red", "WARNING: "),
                ("class:left", "Selecting "),
                ("fg:yellow", "Yes"),
                ("class:left", " Here Will Abort All Current Services Running Under Emmett.")
        ]                    
    return menu_area 

def notif_box(): #Notif box for main menu
    if global_config['setup'] == "True":
        if menuselect_exit == False:
            notif_list = [("underline","Update Info:\n")]
            notif_list.append(("class:left", "Last Updated Kali Containers: "))
            emmetthistory = client.images.get("emmett")
            emmetthistory = emmetthistory.history()
            emmetthistory = list(emmetthistory)[0]
            emmetthistory = emmetthistory["Created"]
            emmetthistory = datetime.fromtimestamp(emmetthistory)
            emmetthistorycheck = datetime.now() - emmetthistory
            if emmetthistorycheck.days > 30:
                emmetthistory = emmetthistory.strftime("%d-%m-%Y")
                notif_list.append(("fg:yellow", emmetthistory+"\n"))
            else:
                emmetthistory = emmetthistory.strftime("%d-%m-%Y")
                notif_list.append(("class:left", emmetthistory+"\n"))

            notif_list.append(("class:left", "Last Updated Burpsuite: "))
            burphistory = os.path.getmtime("./lib/burpsuite.jar")
            burphistory = datetime.fromtimestamp(burphistory)
            burphistorycheck = datetime.now() - burphistory
            if burphistorycheck.days > 30:
                burphistory = burphistory.strftime("%d-%m-%Y")
                notif_list.append(("fg:yellow", burphistory))
            else:
                burphistory = burphistory.strftime("%d-%m-%Y")
                notif_list.append(("class:left", burphistory))
            return notif_list
    


def sessions_menu(): #Sessions Menu
    curreng_object = ConfigParser()
    config_object.read("./config.ini")
    global_config = config_object['GLOBAL']
    if global_config['curreng'] != "None":
        CurrEngFolder = "../Clients/"+global_config['curreng']
        AutoEngConfigLocation = CurrEngFolder+"/data/emmett_config.ini"
        curreng_object.read(AutoEngConfigLocation)
        Eng_Config = curreng_object['ENGINFO']
        try:
            AutoEng_Config = curreng_object['AUTOENG']
        except KeyError:
            curreng_object["AUTOENG"] = {
                "state": "Not Started",
                "engagementnmaptcp": "Not Started",
                "engagementnmapudp": "Not Started",
                "engagementtestssl": "Awaiting TCP Scan Results.",
                "engagementlivehosts": "Not Started",
                "nmaptcp_file": "None"
                }
            with open(AutoEngConfigLocation, 'w') as conf:
                curreng_object.write(conf)
                return
        try:
            Eng_Config['autoeng_toggle']
        except KeyError:
            curreng_object.set("ENGINFO", "autoeng_toggle", "off")
            with open(AutoEngConfigLocation, 'w') as conf:
                curreng_object.write(conf)
                return
        DeloreanBuildVolume = global_config['deloreanpath']+":/root/shared/"
        DocumentsVolume = Path.cwd() / CurrEngFolder
        DocumentsVolume = str(DocumentsVolume)
        DocumentsVolume = DocumentsVolume+":/root/Documents"

        if AutoEng_Config['state'] == "Running": 
            if AutoEng_Config['engagementnmaptcp'] == "Complete" and AutoEng_Config['engagementtestssl'] == "Awaiting TCP Scan Results.": #Check if nmap TCP scan is complete and run testssl if required
                TCPFileCheck = Path(CurrEngFolder+"/output/nmap/"+AutoEng_Config['nmaptcp_file']+".txt")
                if os.stat(TCPFileCheck).st_size != 0:
                    if os.stat(CurrEngFolder+"/data/tls_hosts.txt").st_size == 0:
                        config_object.set('ENGINFO', 'engagementtestssl', 'No TLS host discovered, TestSSL scan not required.')
                    else:
                        now = datetime.now()
                        SSLHTMLFileName = "tls_output_"+now.strftime("%d%m%y_%H%M")+".html"
                        SSLCommand = "/bin/bash -c \"sed -i 's/engagementtestssl = Awaiting TCP Scan Results./engagementtestssl = Running/' /root/Documents/data/emmett_config.ini && cd /root/Documents/output/tls/raw_outputs && testssl --warnings=batch --log --json --file ../../../data/tls_hosts.txt |& tee -a /tmp/"+SSLHTMLFileName+" && cat /tmp/"+SSLHTMLFileName+" | ansi2html > /root/Documents/output/tls/"+SSLHTMLFileName+" && /root/shared/EzModeSSL -d . -o ../"+Eng_Config['client']+" && sed -i 's/engagementtestssl = Running/engagementtestssl = Complete/' /root/Documents/data/emmett_config.ini\""
                        globals()['EngagementTestssl'] = client.containers.run("delorean", SSLCommand, detach=True, remove=True, network_mode="container:Emmett", privileged=False, name="Engagementtestssl", labels=["Emmett","Engagement"], volumes=[DeloreanBuildVolume, DocumentsVolume])
                else:
                    curreng_object.set("ENGINFO", "engagementnmaptcp", "Scan exited with errors, output file empty.")
                    with open(AutoEngConfigLocation, 'w') as conf:
                        curreng_object.write(conf)

        if AutoEng_Config['engagementnmaptcp'] == "Complete" or AutoEng_Config['engagementnmaptcp'] == "Scan exited with errors, output file empty." or AutoEng_Config['engagementnmaptcp'] == "Error: Scan did not complete.":
            if AutoEng_Config['engagementnmapudp'] == "Complete" or AutoEng_Config['engagementnmapudp'] == "Scan exited with errors, output file empty." or AutoEng_Config['engagementnmapudp'] == "Error: Scan did not complete.":
                if AutoEng_Config['engagementtestssl'] == "Complete" or AutoEng_Config['engagementtestssl'] == "No TLS host discovered, TestSSL scan not required." or AutoEng_Config['engagementtestssl'] == "Exited with potential errors, output files empty." or AutoEng_Config['engagementtestssl'] == "Error: Scan did not complete.":
                    if AutoEng_Config['engagementlivehosts'] == "Complete" or AutoEng_Config['engagementlivehosts'] == "Scan complete with no livehosts discovered." or AutoEng_Config['engagementlivehosts'] == "Error: Scan did not complete.":
                        curreng_object.set("AUTOENG", "state", "Complete")
                        with open(AutoEngConfigLocation, 'w') as conf:
                            curreng_object.write(conf)



        ActiveContainerList = [
            ("class:body", "Current Engagement: "),
            ("fg:yellow", global_config['curreng']+"\n\n"),
            ("underline", "Active Containers\n")
        ]
    else:
        ActiveContainerList = [
            ("underline", "Active Containers\n")
        ]
    ActiveContainerName = []
    ContainerList = client.containers.list(filters={"label":"Emmett"})
    for x in ContainerList:
        ContainerName = x.name
        LowerContainerName = ContainerName.lower()
        ContainerStatus = x.status
        ActiveContainerName.append(LowerContainerName)
        if ContainerStatus == "running":
            ActiveContainer = (ContainerName+"\n")
            ActiveContainerList.append(("class:testing", ActiveContainer))
    if ActiveContainerList == [("class:body", "Active Containers:\n")]:
        ActiveContainerList.append(("class:left", "None"))

    
    if global_config['curreng'] != "None":
        if AutoEng_Config['state'] == "Running":
            for x in AutoEng_Config:
                if AutoEng_Config[x] == 'Running':
                    if x == 'state' or x == 'nmaptcp_file':
                        continue
                    if any(x in s for s in ActiveContainerName):
                        continue
                    else:
                        if AutoEng_Config[x] == "Not Started":
                            continue
                        else:
                            curreng_object.set("AUTOENG", x, "Error: Scan did not complete.")
                            with open(AutoEngConfigLocation, 'w') as conf:
                                curreng_object.write(conf)

        if Eng_Config['autoeng_toggle'] == "on": 
            ActiveContainerList.append(("underline", "\nAutoEngagement Progress"))
            ActiveContainerList.append(("class:left", "\n"))                                            
            if AutoEng_Config['state'] != "Not Started":
                ActiveContainerList.append(("class:left", "Nmap TCP Scan: "))
                if AutoEng_Config['engagementnmaptcp'] == "Running":
                    TCPColour = "fg:yellow"
                if AutoEng_Config['engagementnmaptcp'] == "Complete":
                    TCPColour = "fg:green"
                if AutoEng_Config['engagementnmaptcp'] == "Not Started":
                    TCPColour = "class:left"
                if AutoEng_Config['engagementnmaptcp'] == "Scan exited with errors, output file empty." or AutoEng_Config['engagementnmaptcp'] == "Error: Scan did not complete.":
                    TCPColour = "fg:red"
                ActiveContainerList.append((TCPColour, AutoEng_Config['engagementnmaptcp']+"\n"))

                ActiveContainerList.append(("class:left", "Nmap UDP Scan: "))
                if AutoEng_Config['engagementnmapudp'] == "Running":
                    UDPColour = "fg:yellow"
                if AutoEng_Config['engagementnmapudp'] == "Complete":
                    UDPColour = "fg:green"
                if AutoEng_Config['engagementnmapudp'] == "Not Started":
                    UDPColour = "class:left"
                if AutoEng_Config['engagementnmapudp'] == "Scan exited with errors, output file empty." or AutoEng_Config['engagementnmapudp'] == "Error: Scan did not complete.":
                    UDPColour = "fg:red"
                ActiveContainerList.append((UDPColour, AutoEng_Config['engagementnmapudp']+"\n"))

                ActiveContainerList.append(("class:left", "TestSSL: "))
                if AutoEng_Config['engagementtestssl'] == "Awaiting TCP Scan Results.":
                    SSLColour = "class:left"
                if AutoEng_Config['engagementtestssl'] == "Running":
                    SSLColour = "fg:yellow"
                if AutoEng_Config['engagementtestssl'] == "No TLS host discovered, TestSSL scan not required." or AutoEng_Config['engagementtestssl'] == "Complete":
                    SSLColour = "fg:green"
                if AutoEng_Config['engagementtestssl'] == "Exited with potential errors, output files empty." or AutoEng_Config['engagementtestssl'] == "Error: Scan did not complete.":
                    SSLColour = "fg:red"
                ActiveContainerList.append((SSLColour, AutoEng_Config['engagementtestssl']+"\n"))
     

                ActiveContainerList.append(("class:left", "Livehosts Scan: "))
                if AutoEng_Config['engagementlivehosts'] == "Running":
                    LivehostsColour = "fg:yellow"
                if AutoEng_Config['engagementlivehosts'] == "Complete":
                    LivehostsColour = "fg:green"
                if AutoEng_Config['engagementlivehosts'] == "Not Started":
                    LivehostsColour = "class:left"
                if AutoEng_Config['engagementlivehosts'] == "Scan complete with no livehosts discovered." or AutoEng_Config['engagementlivehosts'] == "Error: Scan did not complete.":
                    LivehostsColour = "fg:red"
                ActiveContainerList.append((LivehostsColour, AutoEng_Config['engagementlivehosts']+"\n"))
            else:
                ActiveContainerList.append(("class:left", AutoEng_Config['state']))


    return ActiveContainerList

@Condition
def is_mainmenu():
    return menuselect_main
@Condition
def is_updatemenu():
    return menuselect_update
@Condition
def is_exitmenu():
    return menuselect_exit
@Condition
def is_setupmenu():
    return menuselect_setup

kb = KeyBindings() #Adding Key Bindings to exit main app
@kb.add("1", filter=is_mainmenu) #Key bindings for main menu
def _(event):
    global output
    output = 1
    event.app.exit()
@kb.add("2", filter=is_mainmenu)
def _(event):
    global output
    output = 2
    event.app.exit()
@kb.add("3", filter=is_mainmenu)
def _(event):
    global output
    output = 3
    event.app.exit()
@kb.add("4", filter=is_mainmenu)
def _(event):
    global output
    output = 4
    event.app.exit()
@kb.add("5", filter=is_mainmenu)
def _(event):
    global output
    output = 5
    event.app.exit()
@kb.add("6", filter=is_mainmenu)
def _(event):
    global menuselect_update
    global menuselect_main
    menuselect_main = False
    menuselect_update = True
@kb.add("7", filter=is_mainmenu)
def _(event):
    global menuselect_main
    global menuselect_exit
    menuselect_main = False
    menuselect_exit = True

@kb.add("1", filter=is_updatemenu) #New key bindings for the Update menu selection.
def _(event):
    global update_output
    update_output = 1
    event.app.exit()
@kb.add("2", filter=is_updatemenu)
def _(event):
    global update_output
    update_output = 2
    event.app.exit()
@kb.add("3", filter=is_updatemenu)
def _(event):
    global update_output
    update_output = 3
    event.app.exit()
@kb.add("4", filter=is_updatemenu)
def _(event):
    global menuselect_update
    global menuselect_main
    menuselect_main = True
    menuselect_update = False 

@kb.add("1", filter=is_exitmenu)
def _(event):
    global exit_option
    global output
    global setup_option
    setup_option = 0
    output = 0
    exit_option = 1
    event.app.exit()
@kb.add("2", filter=is_exitmenu)
def _(event):
    global exit_option
    global output
    output = 0
    exit_option = 2
    event.app.exit()
@kb.add("3", filter=is_exitmenu)
def _(event):
    global menuselect_main
    global menuselect_exit
    menuselect_main = True
    menuselect_exit = False

@kb.add("1", filter=is_setupmenu) #Key bindings for setup menu
def _(event):
    global setup_option
    global menuselect_main
    global menuselect_setup
    menuselect_main = True
    menuselect_setup = False
    setup_option = 1
    event.app.exit()
@kb.add("2", filter=is_setupmenu)
def _(event):
    global exit_option
    global setup_option
    setup_option = 2
    exit_option = 1
    event.app.exit()

sessionskb = KeyBindings() #Adding Key Bindings to exit Sessions screen app
@sessionskb.add("c-q") #Key bindings for Sessions screen app
def _(event):
    global menuselect_main
    global menuselect_exit
    global output
    output = 0
    menuselect_main = False
    menuselect_exit = True
    event.app.exit()

@sessionskb.add("c-b")
def _(event):
    global ContainerProgress
    global menuselect_main
    global output
    output = 0
    menuselect_main = True
    ContainerProgress = "Containers State Preserved, Moving to Main Menu."
    event.app.exit()

@sessionskb.add("c-s")
def _(event):
    global menuselect_main
    menuselect_main = False
    event.app.exit()
    
root_container = FloatContainer( #Layout of main application
    content=Window(FormattedTextControl(get_titlebar),
        align=WindowAlign.CENTER),
    floats=[
        Float(
            Window(FormattedTextControl(main_menu),
                align=WindowAlign.LEFT,
                width=59
            ),
            left=0,
            top=15
        ),
        Float(
            Window(FormattedTextControl(notif_box),
                align=WindowAlign.LEFT
            ),
            left=50,
            top=15
        )
    ]
)

application = Application(
    layout=Layout(root_container),
    key_bindings=kb,
    refresh_interval=1,
    color_depth=ColorDepth.DEPTH_24_BIT,
    full_screen=True,
)

sessions_container = FloatContainer(
    content=Window(FormattedTextControl(get_sessionbar),
        align=WindowAlign.CENTER),
    floats=[
        Float(
            
            Window(FormattedTextControl(sessions_menu),
                align=WindowAlign.LEFT,
                width=59
            ),
            left=0,
            top=15
            ),
        Float(
            Window(FormattedTextControl(engagement_scope),
                align=WindowAlign.LEFT
            ),
            left=65,
            top=17
            )
    ]
    )

sessions_application = Application(
    layout=Layout(sessions_container),
    key_bindings=sessionskb,
    refresh_interval=1,
    color_depth=ColorDepth.DEPTH_24_BIT,
    full_screen=True,
)

def run():
    global menuselect_main
    global output
    global update_output
    # Run the interface.
    if output == 0:
        application.run()
    global setup_option

    if menuselect_main == True:
        if output == 1: #Previous Engagement Selection
            output = 0
            if global_config['preveng'] == 'None':
                print("{}".format(colored("ERROR: ", "red", attrs=['bold']))+"No Previous Engagement Data Found, Please Create a New Engagement Or Search For An Existing One.")
                eng_error = input("Press Any Key to Continue.")
                run()
            else:
                PrevEng = global_config['preveng']
                PrevEngList = PrevEng.split("_")
                ClientName = PrevEngList[3]
                DirectoryName = global_config['preveng']
                if os.name == 'nt':
                    GUI = subprocess.Popen("start cmd.exe /c python emmett.py --client "+ClientName+" --eng_dir "+DirectoryName, shell=True)
                else:
                    GUI = subprocess.Popen("xterm -e zsh -c \"python3 emmett.py --client "+ClientName+" --eng_dir "+DirectoryName+"\"", shell=True)
                config_object.set('GLOBAL', 'curreng', DirectoryName)
                with open('./config.ini', 'w') as configfile:
                    config_object.write(configfile)
                output = 5
                run()
        if output == 2: #Search for existing engagement selection
            output = 0
            print("{}".format(colored(assets.logo, "green"))+assets.slogan)
            print("{}".format(colored("Search for Existing Engagement\n", "green", attrs=["underline"])))
            ClientSelectOutcome = emmett.client_selection()
            if ClientSelectOutcome == True:
                output = 5
                run()
                print("Exiting Emmett.")
            else:
                run()
        if output == 3: #Creating new engagement selection
            output = 0
            print("{}".format(colored(assets.logo, "green"))+assets.slogan)
            print("{}".format(colored("Create New Engagement\n", "green", attrs=["underline"])))
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
            NewEngagementOutcome = emmett.new_engagement_creation(ClientName)
            if NewEngagementOutcome == True:
                output = 5
                run()
            else:
                run()
        if output == 4: #VPN only mode selection
            try:
                emmett.vpn_only_mode()
            except:
                pass
            sessions_run()
            run()
        if output == 5: #Open Sessions window selection
            sessions_run()
            if menuselect_main == True or menuselect_exit == True:
                run()
            else:
                curreng_object = ConfigParser()
                if global_config['curreng'] != "None":
                    CurrEngFolder = "../Clients/"+global_config['curreng']
                    AutoEngConfigLocation = CurrEngFolder+"/data/emmett_config.ini"
                    curreng_object.read(AutoEngConfigLocation)
                    Eng_Config = curreng_object['ENGINFO']
                    try:
                        if Eng_Config['autoeng_toggle'] == 'on':
                            curreng_object.set("ENGINFO", "autoeng_toggle", "off")
                        else:
                            curreng_object.set("ENGINFO", "autoeng_toggle", 'on')
                        with open(AutoEngConfigLocation, 'w') as configfile:
                            curreng_object.write(configfile)
                    except KeyError:
                        curreng_object.set("ENGINFO", "autoeng_toggle", 'on')
                        with open(AutoEngConfigLocation, 'w') as configfile:
                            curreng_object.write(configfile)
                menuselect_main = True
                run()
    else:
        if menuselect_update == True:
            if update_output == 1: #Update Kali Image
                containerupdate_status = assets.ui_image_update()
                if containerupdate_status == True:
                    print("{}".format(colored("Kali update complete.", "green")))
                else:
                    print("{}: Kali update failed.".format(colored("ERROR", "red", attrs=["bold"])))    
            if update_output == 2: #Update Burpsuite
                burpupdate_status = assets.ui_burpsuite_update()
                if burpupdate_status == True:
                    print("{}".format(colored("Burpsuite update complete.", "green")))
                else:
                    print("{}: Burpsuite update failed.".format(colored("ERROR", "red", attrs=["bold"])))
            if update_output == 3: #Update both Burp and Kali image
                containerupdate_status = assets.ui_image_update()
                burpupdate_status = assets.ui_burpsuite_update()
                if containerupdate_status == True and burpupdate_status == True:
                    print("{}".format(colored("Kali and Burpsuite update complete.", "green")))
                else:
                    if containerupdate_status == False and burpupdate_status == True:
                        print("{}: Kali update failed.".format(colored("ERROR", "red", attrs=["bold"])))
                        print("{}".format(colored("Burpsuite update complete.", "green")))
                    if containerupdate_status == True and burpupdate_status == False:
                        print("{}".format(colored("Kali update complete.", "green")))
                        print("{}: Burpsuite update failed.".format(colored("ERROR", "red", attrs=["bold"])))
                    if containerupdate_status == False and burpupdate_status == False:
                        print("{}: Kali and Burpsuite updates failed.".format(colored("ERROR", "red", attrs=["bold"])))
            update_input = input("Press Any Key to return to update menu...")
            update_output = 0
            run()

        if menuselect_exit == True:
            if exit_option == 1: #Exit process
                if global_config["setup"] == "True":
                    print("Exiting Containers.")
                    EmmettExit = emmett.sessions_exit()
                    print(EmmettExit)
                    if EmmettExit == "{}".format(colored("Problem Closing All Containers, Manual Interaction Required.", "red")):
                        time.sleep(5)
                    else:
                        time.sleep(1)
                else:
                    print("Setup Cancelled.")
                print("Exiting Emmett.")
            else:
                print("Exiting Emmett,"+"{}".format(colored(" Containers Left Running.", "yellow")))
                time.sleep(2)
            exit()

    if setup_option == 1: #Initial setup run
        assets.batfile_generate()
        kalipull = assets.kali_pull()
        assets.image_create()
        assets.burpsuite_update()
        assets.startupscript_generate()
        config_object.set('GLOBAL', 'setup', 'True')
        config_object.set('GLOBAL', 'preveng', 'None')
        with open('./config.ini', 'w') as configfile:
            config_object.write(configfile)
        print("{}".format(colored("Setup Complete, Entering Emmett.", "green")))
        time.sleep(5)
        ouput = 0
        run()

def sessions_run():
    sessions_application.run()

if __name__ == "__main__":
    run() #Main run point
