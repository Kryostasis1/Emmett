    ___________                       __    __   
    \_   _____/ _____   _____   _____/  |__/  |_ 
     |    __)_ /     \ /     \_/ __ \   __\   __\
     |        \  Y Y  \  Y Y  \  ___/|  |  |  |  
    /_______  /__|_|  /__|_|  /\___  >__|  |__| 
            \/      \/      \/     \/            

A python based engagement tool utilising docker containers

=====Prequisites=====
Emmett current only works on Windows.

Ensure the following is installed:
Python 3.5+
Pip
Docker

=====Docker Setup=====

Once installed ensure that your user is within the Docker user group. To do this in an elevated CMD prompt use "net localgroup docker-users "your-user-id" /ADD

To remove the folder share prompt for each new engagement within the Docker Desktop settings go Resources>File Sharing>"full path to Clients folder" and add. The Clients folder will be automatically created by Emmett in the same parent folder as the Emmett directory.

=====Initial Installation=====

pip install -r requirements.txt

python setup.py (this process can take 30mins-1 hour due to the image creation process)

Copy your OpenVPN files to the directory .\build\ecscproxy\OpenVPN

=====Usage=====

Simply execute Run.bat through CMD, double click the file or create a shortcut to it.

During the engagement creation portion of Emmett you maybe prompted by Windows to allow sharing of the new folder, ensure to click to allow the share each time (see above Docker setup to remove this).

SSH connection binds to port 8008 allowing SOCKS proxy traffic to be tunnelled. To setup Burpsuite to use this install Burpsuite on the Windows host do the following:

User Options > Connections > SOCKS Proxy
Use SOCKS Proxy Enabled
SOCKS proxy host: 127.0.0.1
SOCKS proxy port: 8008

To access ECSC VPN resources install FoxyProxy on a browser and create a proxy using the above info using SOCKS v5.

