import docker
client = docker.from_env()

#Pull Kali Container
print("Pulling Latest Kali Image")
client.images.pull(repository="kalilinux/kali-rolling")