@echo off

pushd %~dp0
python .\scripts\emmett.py
timeout /t 2 /nobreak > nul
ssh -D 8008 -X root@localhost -p 11111 -i "build\ecscproxy\id_rsa" -q
echo Shutting Down Container...
docker rm -f DeLorean