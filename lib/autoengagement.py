from prompt_toolkit.widgets import SearchToolbar, TextArea
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.output.color_depth import ColorDepth
from configparser import ConfigParser
from termcolor import colored
import argparse
import docker
import assets
import subprocess
import os
import time
from datetime import datetime
from pathlib import Path
client = docker.from_env()
now = datetime.now()
config_object = ConfigParser()

#Header
usage_text = 'python autoengagement.py'
example_text = '''Example:
python autoengagement.py --client "example inc"'''
parser = argparse.ArgumentParser(usage=usage_text, epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)

#Arguments
parser.add_argument("--client", help="Provide Client Name.\n")
parser.add_argument("--engdir", help="Provide Engagement Directory.\n")
args = parser.parse_args()

AbsoluteDirectoryName = args.engdir
DocumentsVolume = AbsoluteDirectoryName+":/root/Documents"
AbsoluteBuildName = Path.cwd() / "build/"
AbsoluteBuildName = str(AbsoluteBuildName)
AbsoluteDeLoreanBuildName = AbsoluteBuildName + "/DeLoreans/shared"
DeLoreansBuildVolume = AbsoluteDeLoreanBuildName+":/root/shared/"
ClientName = args.client
ProgressCounter = 0
ConfigFileLocation = AbsoluteDirectoryName+"/data/emmett_config.ini"
config_object.read(ConfigFileLocation)
AutoEng_Config = config_object['AUTOENG']

if AutoEng_Config['state'] != "False":
    config_object.set('ENGINFO', 'autoeng_toggle', 'on')
    config_object.set('AUTOENG', 'state', 'Running')
    config_object.set('AUTOENG', 'engagementnmaptcp', 'Not Started')
    config_object.set('AUTOENG', 'engagementnmapudp', 'Not Started')
    config_object.set('AUTOENG', 'engagementtestssl', 'Awaiting TCP Scan Results.')
    config_object.set('AUTOENG', 'engagementlivehosts', 'Not Started')
    with open(ConfigFileLocation, 'w') as configfile:
        config_object.write(configfile)

TCPNmapFileName = "tcp_output_"+now.strftime("%d%m%y_%H%M")
config_object.set('AUTOENG', 'nmaptcp_file', TCPNmapFileName)
with open(ConfigFileLocation, 'w') as configfile:
    config_object.write(configfile)
TCPNmapCommand = "/bin/bash -c \"sed -i 's/engagementnmaptcp = Not Started/engagementnmaptcp = Running/' /root/Documents/data/emmett_config.ini && nmap -sV -p- -iL /root/Documents/data/hosts.txt -v -oN /root/Documents/output/nmap/raw_outputs/auto_tcp_raw.txt && python /root/shared/tools/parzival.py -f /root/Documents/output/nmap/raw_outputs/auto_tcp_raw.txt -o /root/Documents/output/nmap/"+TCPNmapFileName+" && sed -i 's/engagementnmaptcp = Running/engagementnmaptcp = Complete/' /root/Documents/data/emmett_config.ini\""                   
globals()['EngagementNmapTCP'] = client.containers.run("delorean", TCPNmapCommand, detach=True, remove=False, network_mode="container:Emmett", cap_add=["NET_ADMIN"], privileged=False, name="Engagementnmaptcp", labels=["Emmett","Engagement"], volumes=[DocumentsVolume, DeLoreansBuildVolume])
UDPNmapFileName = "udp_output_"+now.strftime("%d%m%Y_%H%M")
UDPNmapCommand = "/bin/bash -c \"sed -i 's/engagementnmapudp = Not Started/engagementnmapudp = Running/' /root/Documents/data/emmett_config.ini && nmap -sU -iL /root/Documents/data/hosts.txt -v -oN /root/Documents/output/nmap/raw_outputs/auto_udp_raw.txt && python /root/shared/tools/parzival.py -f /root/Documents/output/nmap/raw_outputs/auto_udp_raw.txt -o /root/Documents/output/nmap/"+UDPNmapFileName+" && sed -i 's/engagementnmapudp = Running/engagementnmapudp = Complete/' /root/Documents/data/emmett_config.ini\""
globals()['EngagementNmapUDP'] = client.containers.run("delorean", UDPNmapCommand, detach=True, remove=False, network_mode="container:Emmett", cap_add=["NET_ADMIN"], privileged=False, name="Engagementnmapudp", labels=["Emmett", "Engagement"], volumes=[DocumentsVolume, DeLoreansBuildVolume])                      
globals()['Livehosts'] = client.containers.run("delorean", "/bin/sh -c \"sed -i 's/engagementlivehosts = Not Started/engagementlivehosts = Running/' /root/Documents/data/emmett_config.ini && nmap -p- --open -iL /root/Documents/data/hosts.txt -oG - | grep '/open' | awk '{ print $2 }' > /root/Documents/output/nmap/auto_livehosts.txt && sed -i 's/engagementlivehosts = Running/engagementlivehosts = Complete/' /root/Documents/data/emmett_config.ini\"", detach=True, remove=True, network_mode="container:Emmett", privileged=False, name="Engagementlivehosts", labels=["Emmett", "Engagement"], volumes=[DocumentsVolume])
