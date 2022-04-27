import docker
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
client = docker.from_env()

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

#Pull Kali Container
print("Pulling Latest Kali Image")
client.images.pull(repository="kalilinux/kali-rolling")

#Creating Docker Image
print("Building Docker Image. This Can Take 15-30 Minutes Depending On PC Performance")
client.images.build(path="build\\", tag="emmett", rm=True)
print("Docker Image Created Successfully")

#Creating SSH Keys
key = rsa.generate_private_key(
	public_exponent=65537,
	key_size=4096
)

private_key = key.private_bytes(
    crypto_serialization.Encoding.PEM,
    crypto_serialization.PrivateFormat.PKCS8,
    crypto_serialization.NoEncryption()
)

public_key = key.public_key().public_bytes(
    crypto_serialization.Encoding.OpenSSH,
    crypto_serialization.PublicFormat.OpenSSH
)

private_key_file = open("build\\ecscproxy\\id_rsa", "w")
private_key_file.write(private_key.decode())
private_key_file.close()

public_key_file = open("build\\ecscproxy\\id_rsa.pub", "w")
public_key_file.write(public_key.decode())
public_key_file.close()

public_key_file = open("build\\ecscproxy\\authorized_keys", "w")
public_key_file.write(public_key.decode())
public_key_file.close()

print("SSH Keys Created")
print()

#OVPN Setup
VPNFileName = input("What Is The OpenVPN FileName (inc .ovpn extension)?")
StartupScript = open('build\\ecscproxy\\ecsc-startup.sh', 'a')
StartupScript.write('\ncd /root/shared/OpenVPN && openvpn '+VPNFileName)
StartupScript.close()
print("Ensure You Copy OpenVPN Connection Files To \\build\\ecscproxy\\OpenVPN\\")