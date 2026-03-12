FROM kalilinux/kali-rolling:latest
EXPOSE 8118/tcp 
RUN apt -y update && apt -y upgrade && apt install -y openvpn && apt install -y privoxy && apt install -y dos2unix expect

ENTRYPOINT ["/root/shared/startup.sh"]