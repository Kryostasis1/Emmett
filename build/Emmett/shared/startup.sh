#!/bin/bash
cp /root/shared/motd /etc/motd
echo 'cat /root/shared/motd' >> /root/.bashrc
tail -f /dev/null
        