from __main__ import *
import docker
import subprocess
import re
import argparse
import sys
import getpass
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from os import getlogin, replace
from configparser import ConfigParser
from termcolor import colored
from urllib.request import urlretrieve
client = docker.from_env()

logo = ("""

___________                       __    __   
\\_   _____/ _____   _____   _____/  |__/  |_ 
 |    __)_ /     \\ /     \\_/ __ \\   __\\   __\\
 |        \\  Y Y  \\  Y Y  \\  ___/|  |  |  |  
/_______  /__|_|  /__|_|  /\\___  >__|  |__| 
        \\/      \\/      \\/     \\/            """)

slogan = ("""v2.1.16
The Way I See It, If You're Gonna Build An Engagement, Why Not Do It With Some Style?


    """)

app_logo = ("""

___________                       __    __   
\\_   _____/ _____   _____   _____/  |__/  |_ 
 |    __)_ /     \\ /     \\_/ __ \\   __\\   __\\
 |        \\  Y Y  \\  Y Y  \\  ___/|  |  |  |  
/_______  /__|_|  /__|_|  /\\___  >__|  |__| 
              \\/      \\/      \\/     \\/            v2.1.16
    """)

app_slogan = ("""The Way I See It, If You're Gonna Build An Engagement, Why Not Do It With Some Style?

""")

#Sanitize Regex
regex = '^[a-zA-Z0-9 -_!\"£$=+]+$'
ovpn_regex = '^[a-zA-Z0-9 -_!\"£$=+.]+$'
scope_regex = '^[a-zA-Z0-9 -_!\"£$=+./:]+$'
url_regex = '(http(s)?:\\/\\/[a-zA-Z0-9\\.\\-\\_\\/]+)'

#Docker Functions
def kali_pull():
        #Pull Kali Image
        print("Pulling Latest Kali Image")
        client.images.pull(repository="kalilinux/kali-rolling:latest")
        return True

def image_create():
         #Creating Emmett Image
        print("Building Docker Image. This Can Take 15-30 Minutes Depending On PC Performance")
        client.images.build(path="build/Emmett", tag="emmett", rm=True, nocache=True, quiet=False)
        client.images.build(path="build/DeLoreans", tag="delorean", rm=True, nocache=True, quiet=False)
        print("{}".format(colored("Docker Images Created Successfully", "green")))

        #Remove Kali Images
        print("Cleaning Up Images")
        client.images.remove(image="kalilinux/kali-rolling:latest")

def image_update():
    #Updating Existing Image OS
    try:
        print("Checking for previous Emmett image.")
        dockercheck = client.images.list(name="emmett")
        dockercheck2 = client.images.list(name="delorean")
        
        if len(dockercheck) > 0:
            print("Previous Emmett image located.")
            print("Updating Emmett image.")
            EmmettUpdate = client.images.build(path="lib/update/Emmett/", tag="emmett", rm=True)
            for item in EmmettUpdate[1]:
                for key, value in item.items():
                    if key == 'stream':
                        text = value.strip()
                        if text:
                            print(text)
            print("{}".format(colored("Emmett Update successful.", "green")))
        else:
            print("No previous Emmett image found.")

        if len(dockercheck2) > 0:
            print("Previous DeLorean image located.")
            print("Updating DeLorean image.")
            DeloreanUpdate = client.images.build(path="lib/update/DeLoreans/", tag="delorean", rm=True)
            for item in DeloreanUpdate[1]:
                for key, value in item.items():
                    if key == 'stream':
                        text = value.strip()
                        if text:
                            print(text)
            print("{}".format(colored("Delorean Update successful.", "green")))
        else:
            print("No previous DeLorean image found.")
    except:
        print("{}".format(colored("Error Updating.", "red", attrs=["bold"])))

def ui_image_update():
    try:
        print("Checking for previous Emmett image.")
        dockercheck = client.images.list(name="emmett")
        dockercheck2 = client.images.list(name="delorean")
        
        if len(dockercheck) > 0:
            print("Previous Emmett image located.")
            print("Updating Emmett image.")
            EmmettUpdate = client.images.build(path="lib/update/Emmett/", tag="emmett", rm=True)
            for item in EmmettUpdate[1]:
                for key, value in item.items():
                    if key == 'stream':
                        text = value.strip()
                        if text:
                            print(text)
            print("{}".format(colored("Emmett Update successful.", "green")))
        else:
            print("No previous Emmett image found.")

        if len(dockercheck2) > 0:
            print("Previous DeLorean image located.")
            print("Updating DeLorean image.")
            DeloreanUpdate = client.images.build(path="lib/update/DeLoreans/", tag="delorean", rm=True)
            for item in DeloreanUpdate[1]:
                for key, value in item.items():
                    if key == 'stream':
                        text = value.strip()
                        if text:
                            print(text)
            print("{}".format(colored("Delorean Update successful.", "green")))
        else:
            print("No previous DeLorean image found.")
        return True
    except:
        return False

def burpsuite_update():
    #Updating or initially downloading Burpsuite file
    LATEST_VER_URL = "https://portswigger.net/burp/releases/professional/latest"
    DOWNLOAD_URL = "https://portswigger.net/burp/releases/download?product=pro&version={}&type=jar"
    burphtml = requests.get(LATEST_VER_URL)
    burpcontent = BeautifulSoup(burphtml.text, features="lxml")
    # get latest burp version from page text
    version_heading = burpcontent.find('h1').get_text()
    version_split = version_heading.split()
    latest_version = version_split[4]
    print(latest_version)
    print("Downloading latest Burpsuite JAR file.")
    burpurl = DOWNLOAD_URL.format(latest_version)
    burpfilename = "lib/burpsuite.jar"
    urlretrieve(burpurl, burpfilename)

def ui_burpsuite_update():
    #Updating or initially downloading Burpsuite file
    try:
        LATEST_VER_URL = "https://portswigger.net/burp/releases/professional/latest"
        DOWNLOAD_URL = "https://portswigger.net/burp/releases/download?product=pro&version={}&type=jar"
        burphtml = requests.get(LATEST_VER_URL)
        burpcontent = BeautifulSoup(burphtml.text, features="lxml")
        # get latest burp version from page text
        version_heading = burpcontent.find('h1').get_text()
        version_split = version_heading.split()
        latest_version = version_split[3]
        print(latest_version)
        print("Downloading latest Burpsuite JAR file.")
        burpurl = DOWNLOAD_URL.format(latest_version)
        burpfilename = "lib/burpsuite.jar"
        urlretrieve(burpurl, burpfilename)
        return True
    except:
        return False

#Startup Script Functions
VPNFileExt = ".ovpn"
def startupscript_generate(VPNMFA=None, VPN_Status=None):
    #Startup Script Setup
    config_object = ConfigParser()
    config_object.read("./config.ini")
    StartupFile = Path("build/Emmett/shared/startup.sh")
    DeLoreanStartupFile = Path("build/DeLoreans/shared/startup.sh")
    NoVPNEmmettStartupFile = Path("build/Emmett/shared/novpnstartup.sh")
    if VPN_Status == None:
        VPN_Status = input ("Do you want to setup Emmett with a VPN? (Y/N Default:Y):")
        VPN_Status = VPN_Status.replace(" ", "")
        VPN_Status = VPN_Status.lower()
        NoVPNEmmettStartupScript = open('build/Emmett/shared/novpnstartup.sh', 'w')
        NoVPNEmmettStartupScript.write("""#!/bin/bash
rm /etc/privoxy/config
cp /root/shared/config /etc/privoxy/config
privoxy --pidfile /var/run/privoxy.pid /etc/privoxy/config
cp /root/shared/motd /etc/motd
echo 'cat /root/shared/motd' >> /root/.bashrc
cp /root/shared/resolv.conf /etc/resolv.conf
tail -f /dev/null""")
        NoVPNEmmettStartupScript.close()
        if VPN_Status == 'n':
            config_object.set('VPN', 'status', 'Disabled')
            config_object.set('VPN', 'mfa', 'False') 
        else:
            VPN_Status = 'y'
            config_object.set('VPN', 'status', 'Enabled')
        with open('./config.ini', 'w') as configfile:
            config_object.write(configfile)
    if VPNMFA != "Ignore" and (VPN_Status == "y" or (VPN_Status == "n" and StartupFile.is_file())):        
        EmmettStartupScript = open('build/Emmett/shared/startup.sh', 'w')
        while True:
            VPNFileName = input("What Is The OpenVPN FileName? (excluding extension)")
            if VPNMFA == None:
                VPNMFA = input("Does the VPN Require MFA? (Y/N Default:N): ")
                VPNMFA = VPNMFA.replace(" ", "")
                VPNMFA = VPNMFA.lower()
            if VPNMFA == "y": #Updating Config file if MFA is present or not on VPN
                config_object.set('VPN', 'mfa', 'True')
            else:
                config_object.set('VPN', 'mfa', 'False')
            with open('./config.ini', 'w') as configfile:
                config_object.write(configfile)
            if VPNFileName:
                if VPNFileExt in VPNFileName:
                    if re.match(ovpn_regex, VPNFileName):
                        config_object.set('VPN', 'filename', VPNFileName)
                        with open('./config.ini', 'w') as configfile:
                            config_object.write(configfile)
                        break
                if re.match(ovpn_regex, VPNFileName): #Checking user input for bad characters
                    VPNFileName = VPNFileName+VPNFileExt
                    config_object.set('VPN', 'filename', VPNFileName)
                    with open('./config.ini', 'w') as configfile:
                        config_object.write(configfile)
                    break
                else:
                    print("{}".format(colored("ERROR: ", "red", attrs=["bold"]))+"Invalid Characters Entered.")
        if VPNMFA == 'y': #Different Startup Scripts Dependent on in MFA is Present on VPN
            VPNUsername = input("What is your VPN Username?")
            EmmettStartupScript.write("""#!/bin/bash
rm /etc/privoxy/config
cp /root/shared/config /etc/privoxy/config
privoxy --pidfile /var/run/privoxy.pid /etc/privoxy/config
cp /root/shared/motd /etc/motd
echo 'cat /root/shared/motd' >> /root/.bashrc
cp /root/shared/resolv.conf /etc/resolv.conf
echo "Starting VPN connection..."
expect <<'EOF' 
spawn openvpn --config /root/shared/OpenVPN/"""+VPNFileName+""" 
expect "Username:"
send \""""+VPNUsername+"""\\r" 
expect "Password:"
send "$env(VPN_PASSWORD)\\r" 
expect "CHALLENGE:"
send "$env(VPN_MFA)\\r" 
interact 
EOF

# Keep container alive
tail -f /dev/null""")
            EmmettStartupScript.close()
        else:
            EmmettStartupScript.write("""#!/bin/bash
rm /etc/privoxy/config
cp /root/shared/config /etc/privoxy/config
privoxy --pidfile /var/run/privoxy.pid /etc/privoxy/config
cp /root/shared/motd /etc/motd
echo 'cat /root/shared/motd' >> /root/.bashrc
cp /root/shared/resolv.conf /etc/resolv.conf
cd /root/shared/OpenVPN && openvpn """+VPNFileName)        
        EmmettStartupScript.close()
        print("{}".format(colored("Ensure You Copy OpenVPN Connection Files To build/Emmett/shared/OpenVPN/", "yellow")))
    else:
        if not NoVPNEmmettStartupFile.is_file():
            NoVPNEmmettStartupScript = open('build/Emmett/shared/novpnstartup.sh', 'w')
            NoVPNEmmettStartupScript.write("""#!/bin/bash
rm /etc/privoxy/config
cp /root/shared/config /etc/privoxy/config
privoxy --pidfile /var/run/privoxy.pid /etc/privoxy/config
cp /root/shared/motd /etc/motd
echo 'cat /root/shared/motd' >> /root/.bashrc
cp /root/shared/resolv.conf /etc/resolv.conf
tail -f /dev/null""")        
            NoVPNEmmettStartupScript.close()

    if not DeLoreanStartupFile.is_file():
        DeLoreanStartupScript = open('build/DeLoreans/shared/startup.sh', 'w')
        DeLoreanStartupScript.write("""#!/bin/bash
    echo 'cat /root/shared/motd' >> /root/.bashrc
    tail -f /dev/null""")
        DeLoreanStartupScript.close()
    DeloreanDos2Unix = DeLoreanStartupFile.read_bytes()
    DeloreanDos2Unix = DeloreanDos2Unix.replace(b'\r\n', b'\n')
    DeLoreanStartupFile.write_bytes(DeloreanDos2Unix)

    NoVPNStartupDos2Unix = NoVPNEmmettStartupFile.read_bytes()
    NoVPNStartupDos2Unix = NoVPNStartupDos2Unix.replace(b'\r\n', b'\n')
    NoVPNEmmettStartupFile.write_bytes(NoVPNStartupDos2Unix)

    if StartupFile.is_file():
        StartupFileDos2Unix = StartupFile.read_bytes()
        StartupFileDos2Unix = StartupFileDos2Unix.replace(b'\r\n', b'\n')
        StartupFile.write_bytes(StartupFileDos2Unix)

def batfile_generate(): #Creating run.bat file
    PythonExePath = sys.executable
    EmmettDirPath = Path.cwd() / "."
    EmmettDirPath = str(EmmettDirPath)
    EmmettFilePath = EmmettDirPath+"/run.py"
    BatFilePath = EmmettDirPath+"/run.bat"
    BatFile = open(BatFilePath, 'w')
    BatFile.write("@echo off\n\""""+PythonExePath+"\" \""+EmmettFilePath+"\"")
    print("{}".format(colored("run.bat file generated in Emmett directory, this can be used to pin Emmett to Start Menu or to simplify boot process.", "yellow")))


#Uninstall
def uninstall():
    username = getlogin()
    while True:
        WarningDecision = input("{}".format(colored("WARNING: ", "red", attrs=["bold"]))+"This Script Will Delete The Docker Images Created By Emmetts Setup Process. Continue? (Y/N)")
        WarningDecision = WarningDecision.replace(" ", "")
        WarningDecision = WarningDecision.lower()
        if WarningDecision in ("y","n"):
            break
    if WarningDecision == "y":
        print("Attempting To Remove Emmett Image.")
        try:
            client.images.remove(image="emmett")
            print("{}".format(colored("Removed Successfully.", "green")))
        except:
            print("{}".format(colored("ERROR: ", "red", attrs=["bold"]))+"No Emmett Image Was Found.")

        print("Attempting To Remove DeLorean Image.")
        try:
            client.images.remove(image="delorean")
            print("{}".format(colored("Removed Successfully.", "green")))
        except:
            print("{}".format(colored("ERROR: ", "red", attrs=["bold"]))+"No DeLorean Image Was Found.")
        config_object = ConfigParser()
        config_object.read("./config.ini")
        config_object.set('GLOBAL', 'setup', 'False')
        with open('./config.ini', 'w') as configfile:
            config_object.write(configfile)

#Emmett Container Status Check
def emmett_status():
    try:
        container = client.containers.get("Emmett")
        if container.status == "running":
            ToggleCheck = input("Active Emmett session detected, do you want to restart this session? (Y/N Default:N): ")
            ToggleCheck = ToggleCheck.replace(" ", "")
            ToggleCheck = ToggleCheck.lower()
            if ToggleCheck == "y":
                KillProcess = subprocess.run(['docker', 'container', 'kill', 'Emmett'], capture_output=True, text=True)
                ContainerKillCheck = KillProcess.stderr
                if ContainerKillCheck == "":
                    print("Successfully stopped container.")
                    return True
                else:
                    print("{}: ".format(colored("ERROR", "red", attrs=["bold"]))+ContainerKillCheck)
            else:
                return False
    except docker.errors.NotFound:
        return False

#Starting Emmett
def emmett_startup(VPNMFA=None, VPN_Status=None):
    AbsoluteBuildName = Path.cwd() / "build/"
    AbsoluteBuildName = str(AbsoluteBuildName)
    AbsoluteEmmettBuildName = AbsoluteBuildName + "/Emmett/shared"
    EmmettBuildVolume = AbsoluteEmmettBuildName+":/root/shared/"
    if VPN_Status == "y":
        if VPNMFA == "True":
            VPNPassword = getpass.getpass("VPN Password: ")
            VPNmfa = input("MFA Code: ")
            try:
                EmmettContainer = client.containers.run("emmett", detach=True, remove=True, entrypoint=["/bin/bash","/root/shared/startup.sh"], devices=["/dev/net/tun"], cap_add=["NET_ADMIN"], privileged=False, name="Emmett", labels=["Emmett"], ports={'8118':'8118'}, volumes=[EmmettBuildVolume], environment={"VPN_PASSWORD": VPNPassword, "VPN_MFA": VPNmfa})
            except docker.errors.APIError:
                pass
        else:
            try:
                EmmettContainer = client.containers.run("emmett", detach=True, remove=True, entrypoint=["/bin/bash","/root/shared/startup.sh"], devices=["/dev/net/tun"], cap_add=["NET_ADMIN"], privileged=False, name="Emmett", labels=["Emmett"], ports={'8118':'8118'}, volumes=[EmmettBuildVolume])
            except docker.errors.APIError:
                pass
    else:
            try:
                EmmettContainer = client.containers.run("emmett", detach=True, remove=True, entrypoint=["/bin/bash","/root/shared/novpnstartup.sh"], devices=["/dev/net/tun"], cap_add=["NET_ADMIN"], privileged=False, name="Emmett", labels=["Emmett"], ports={'8118':'8118'}, volumes=[EmmettBuildVolume])
            except docker.errors.APIError:
                pass
    print("{}".format(colored("Successfully started container.", "green")))