#!/bin/bash

rm /etc/privoxy/config
cp /root/shared/config /etc/privoxy/config
privoxy --pidfile /var/run/privoxy.pid /etc/privoxy/config
echo "root:toor1" | chpasswd
mkdir /root/.ssh/ && chmod 0700 /root/.ssh/
sed -i 's/^#PermitRootLogin/PermitRootLogin/g' /etc/ssh/sshd_config
sed -i 's/^#PubkeyAuthentication/PubkeyAuthentication/g' /etc/ssh/sshd_config
sed -i '/^PermitRootLogin/s/prohibit-password/yes/' /etc/ssh/sshd_config
cp /root/shared/motd /etc/motd
cp /root/shared/authorized_keys /root/.ssh/authorized_keys
cp /root/shared/known_hosts /root/.ssh/known_hosts
chmod 0600 /root/.ssh/authorized_keys
chmod 0600 /root/.ssh/known_hosts
chmod 0600 /etc/ssh/ssh_host_rsa_key
chmod 0600 /etc/ssh/ssh_host_ecdsa_key
chmod 0600 /etc/ssh/ssh_host_ed25519_key
service ssh restart
whoami