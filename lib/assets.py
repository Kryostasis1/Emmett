from __main__ import *
import docker
import re
import argparse
from pathlib import Path
from os import getlogin, replace
client = docker.from_env()

logo = ("""

___________                       __    __   
\\_   _____/ _____   _____   _____/  |__/  |_ 
 |    __)_ /     \\ /     \\_/ __ \\   __\\   __\\
 |        \\  Y Y  \\  Y Y  \\  ___/|  |  |  |  
/_______  /__|_|  /__|_|  /\\___  >__|  |__| 
        \\/      \\/      \\/     \\/            v2.0.1
The Way I See It, If You're Gonna Build An Engagement, Why Not Do It With Some Style?


    """)

#Sanitize Regex
regex = '^[a-zA-Z0-9\ \-\_\!\"\£\$\=\+]+$'
ovpn_regex = '^[a-zA-Z0-9\ \-\_\!\"\£\$\=\+\.]+$'
scope_regex = '^[a-zA-Z0-9\ \-\_\!\"\£\$\=\+\.\/\:]+$'

#Docker Functions
def kali_pull():
        #Pull Kali Image
        print("Pulling Latest Kali Image")
        client.images.pull(repository="kalilinux/kali-rolling:latest")

def image_create():
         #Creating Emmett Image
        print("Building Docker Image. This Can Take 15-30 Minutes Depending On PC Performance")
        client.images.build(path="build/Emmett", tag="emmett", rm=True)
        client.images.build(path="build/DeLoreans", tag="delorean", rm=True)
        print("Docker Images Created Successfully")

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
            client.images.build(path="lib/update/Emmett/", tag="emmett", rm=True)
            print("Emmett Update successful.")
        else:
            print("No previous Emmett image found.")

        if len(dockercheck2) > 0:
            print("Previous DeLorean image located.")
            print("Updating DeLorean image.")
            client.images.build(path="lib/update/DeLoreans/", tag="delorean", rm=True)
            print("Delorean Update successful.")
        else:
            print("No previous DeLorean image found.")
    except:
        print("Error Updating.")

#Startup Script Functions
VPNFileExt = ".ovpn"
def startupscript_generate():
    #Startup Script Setup
    while True:
        VPNFileName = input("What Is The OpenVPN FileName? (excluding extension)")
        if VPNFileName:
            if VPNFileExt in VPNFileName:
                if re.match(ovpn_regex, VPNFileName):
                    break
            if re.match(ovpn_regex, VPNFileName): #Checking user input for bad characters
                VPNFileName = VPNFileName+VPNFileExt
                break
            else:
                print("Invalid Characters Entered.")
    EmmettStartupScript = open('build/Emmett/shared/startup.sh', 'w')
    EmmettStartupScript.write("""#!/bin/bash
rm /etc/privoxy/config
cp /root/shared/config /etc/privoxy/config
privoxy --pidfile /var/run/privoxy.pid /etc/privoxy/config
cp /root/shared/motd /etc/motd
echo 'cat /root/shared/motd' >> /root/.bashrc
cd /root/shared/OpenVPN && openvpn """+VPNFileName)
    EmmettStartupScript.close()

    DeLoreanStartupScript = open('build/DeLoreans/shared/startup.sh', 'w')
    DeLoreanStartupScript.write("""#!/bin/bash
echo 'cat /root/shared/motd' >> /root/.bashrc
tail -f /dev/null""")
    DeLoreanStartupScript.close()
    print("Ensure You Copy OpenVPN Connection Files To build/Emmett/shared/OpenVPN/")

#Uninstall
def uninstall():
    username = getlogin()
    while True:
        WarningDecision = input("WARNING: This Script Will Delete The Docker Images Created By Emmetts Setup Process. Continue? (Y/N)")
        WarningDecision = WarningDecision.replace(" ", "")
        WarningDecision = WarningDecision.lower()
        if WarningDecision in ("y","n"):
            break
    if WarningDecision == "y":
        print("Attempting To Remove Emmett Image.")
        try:
            client.images.remove(image="emmett")
            print("Removed Successfully.")
        except:
            print("No Emmett Image Was Found.")

        print("Attempting To Remove DeLorean Image.")
        try:
            client.images.remove(image="delorean")
            print("Removed Successfully.")
        except:
            print("No DeLorean Image Was Found.")

