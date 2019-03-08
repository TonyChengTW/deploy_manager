#!/bin/bash
# Author:Tony <tony.cheng@104.com.tw>

apt update
apt install -y curl
cd /root
export MY_MAC=$(ip a | grep ether| head -1 | awk '{print $2}' | tr -d '\n')
export MY_DEV=$(ip a | grep BROADCAST| head -1 | awk '{print $2}' | sed -e 's/://' | tr -d '\n')
curl http://192.168.178.178:7878/ip_mapper?mac=$MY_MAC > /tmp/my_mgmt_ip.txt
export MY_MGMT_IP=$(cat /tmp/my_mgmt_ip.txt|sed -e 's/\"//g')
ip address add $MY_MGMT_IP/24 dev $MY_DEV
