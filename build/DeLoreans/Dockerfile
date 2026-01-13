FROM kalilinux/kali-rolling
ENV DEBIAN_FRONTEND=noninteractive
RUN apt -y update && apt -y upgrade && apt install -y kali-linux-headless && apt install -y build-essential && apt install -y net-tools iputils-ping wget curl locate smbclient nano testssl.sh dos2unix pipx humble sublist3r
RUN pipx install ansi2html
CMD dos2unix /root/shared/startup.sh && bash /root/shared/startup.sh