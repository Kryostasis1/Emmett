    ___________                       __    __   
    \_   _____/ _____   _____   _____/  |__/  |_ 
     |    __)_ /     \ /     \_/ __ \   __\   __\
     |        \  Y Y  \  Y Y  \  ___/|  |  |  |  
    /_______  /__|_|  /__|_|  /\___  >__|  |__|  
            \/      \/      \/     \/            v2.0.1
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

6. Copy your OpenVPN files to the directory ./build/proxy/OpenVPN

## Windows Installation

1. Install latest version of Docker Desktop https://www.docker.com/products/docker-desktop/

2. Once installed ensure that your user is within the Docker user group. To do this, open an elevated CMD and use `net localgroup docker-users "your-user-id" /ADD`

3. `pip install -r requirements.txt`

4. `python emmett.py --setup`

6. Copy your OpenVPN files to the directory .\build\proxy\OpenVPN

# OSX  
  
Similar install to linux above, but for Docker, ensure you install and 
run to fix the missing socket/daemon issue acknowledged here 
(https://github.com/docker/for-mac/issues/6531): 

```sudo ln -s "$HOME/.docker/run/docker.sock" /var/run/docker.sock```  
  
Note: This was tested only on an M2 macbook, not sure if this will apply 
for other models.

# Usage

python emmett.py

During the engagement creation portion of Emmett you maybe prompted in Windows to allow sharing of the new folder, to disable this add the Clients folder to File Sharing in Docker Desktop.

## Emmett CLI Command List
```connect - Open a bash session on container.
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
```	


# Tips & Info

Privoxy is running over port 8118. In order to use Burpsuite with this you must install Burpsuite on your base (or whatever you're going to be running Emmett from) and do the following in Burp:

User Options > Connections > Upstream Proxy Servers\
Add\
Proxy host: 127.0.0.1\
Proxy port: 8008\

To access VPN resources install FoxyProxy on a browser and create a proxy using the above info using SOCKS v5.

# Troubleshooting

Check the below to see if any of these can help. If not, throw me a message and i'll be happy to assist.

Setup phase hanging on container creation? This process can take a long time and depends on both your internet connection speed and PC setup due to it downloading roughly 8gb of apps to build the container images. That said if it has been running over an hour try hitting the enter key as the terminal output can sometimes hang.

# Uninstall

`python emmett.py --uninstall`
