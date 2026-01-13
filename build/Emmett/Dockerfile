FROM kalilinux/kali-rolling:latest
EXPOSE 8118/tcp 
RUN apt -y update && apt -y upgrade && apt install -y openvpn && apt install -y privoxy && apt install dos2unix
CMD dos2unix /root/shared/startup.sh && bash /root/shared/startup.sh