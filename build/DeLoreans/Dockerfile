FROM kalilinux/kali-rolling:latest
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y kali-linux-headless && apt install -y build-essential && apt install -y net-tools && apt install -y iputils-ping && apt install -y wget && apt install -y curl locate smbclient && apt install -y nano && apt install -y testssl.sh
CMD dos2unix /root/shared/startup.sh && bash /root/shared/startup.sh