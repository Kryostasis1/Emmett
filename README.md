    ___________                       __    __   
    \_   _____/ _____   _____   _____/  |__/  |_ 
     |    __)_ /     \ /     \_/ __ \   __\   __\
     |        \  Y Y  \  Y Y  \  ___/|  |  |  |  
    /_______  /__|_|  /__|_|  /\___  >__|  |__|  
            \/      \/      \/     \/            v2.1.9
A Docker based engagement tool. Emmett makes managing engagements easy, ensuring you are using a fresh Kali box for each engagement. Keeping your testing machine clean from previous client data while minimising the storage and resource usage that comes with the standard VM testing route.

# Prerequisites

Ensure the following is installed:
 - Python 3.5+
 - Pip
 - Docker

# Install

## Linux 

1. Install latest version of Docker https://docs.docker.com/engine/install/ubuntu/

2. Complete post-installation step to manage docker as a non-root user https://docs.docker.com/engine/install/linux-postinstall/

3. `pip install -r requirements.txt`

4. `python3 emmett.py --setup` (this process can take 30 mins - 1 hour due to the image creation process)

6. Copy your OpenVPN files to the directory ./build/Emmett/shared/OpenVPN/

## Windows Installation

1. Install latest version of Docker Desktop https://www.docker.com/products/docker-desktop/

2. Once installed ensure that your user is within the Docker user group. To do this, open an elevated CMD and use `net localgroup docker-users "your-user-id" /ADD`

3. `pip install -r requirements.txt`

4. `python run.py`

5. Copy your OpenVPN files to the directory .\build\Emmett\shared\OpenVPN\

# Usage

`run.bat` or `python run.py`

During the engagement creation portion of Emmett you maybe prompted in Windows to allow sharing of the new folder, to disable this add the Clients folder to File Sharing in Docker Desktop.

## Emmett CLI Command List
```
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
```	


# Tips & Info

Privoxy is running over port 8118. In order to use Burpsuite with this you must configure the following in Burp:

User Options > Connections > Upstream Proxy Servers\
Add\
Proxy host: 127.0.0.1\
Proxy port: 8118\

To access VPN resources install FoxyProxy on a browser and create a proxy using the above info using HTTP.

# Troubleshooting

Check the below to see if any of these can help. If not, throw me a message and i'll be happy to assist.

Setup phase hanging on container creation? This process can take a long time and depends on both your internet connection speed and PC setup due to it downloading roughly 8gb of apps to build the container images. That said if it has been running over an hour try hitting the enter key as the terminal output can sometimes hang.

Emmett container failing to run? Check that your VPN file is configured correctly (or ovpn files may need adjusting to allow deprecated ciphers to work on new version of openvpn.)

# Uninstall

`python emmett.py --uninstall`