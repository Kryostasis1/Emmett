FROM kalilinux/kali-rolling:latest
EXPOSE 8118/tcp
EXPOSE 22/tcp
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y kali-linux-headless && apt install -y openconnect && apt install -y privoxy && apt install -y build-essential && apt install -y net-tools && apt install -y iputils-ping && apt install -y wget && apt install -y curl locate smbclient && apt install -y nano && apt install -y testssl.sh
CMD bash /root/shared/ecsc-startup.sh