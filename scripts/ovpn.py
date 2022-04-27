#OVPN Setup
VPNFileName = input("What Is The OpenVPN FileName (inc extension)?")
StartupScript = open('build\\ecscproxy\\ecsc-startup.sh', 'a')
StartupScript.write('\ncd /root/shared/OpenVPN && openvpn '+VPNFileName)
StartupScript.close()