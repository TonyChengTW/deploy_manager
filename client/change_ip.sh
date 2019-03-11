#!/bin/bash
# Author:Tony <tony.cheng@104.com.tw>

cd /root
export MY_MAC=$(ip a | grep ether| head -1 | awk '{print $2}' | tr -d '\n')
export MY_DEV=$(ip a | grep BROADCAST| head -1 | awk '{print $2}' | sed -e 's/://' | tr -d '\n')
curl http://192.168.178.178:7878/ip_mapper?mac=$MY_MAC > /tmp/my_mgmt_ip.txt
export MY_MGMT_IP=$(cat /tmp/my_mgmt_ip.txt|grep -v 'not'|sed -e 's/\"//g')
if [ -z $MY_MGMT_IP ]; then
    echo 'no mgmt IP is get from deploy manager, please check ip_manager.ini' > /root/mgmt_ip.log
    exit 1
fi

echo "MY_MGMT_IP=$MY_MGMT_IP"

export MY_IP_IS_SET=$(ip a | grep $MY_MGMT_IP | wc -l)
echo "MY_IP_IS_SET=$MY_IP_IS_SET"

if [ $MY_IP_IS_SET -eq 1 ]; then
    crontab -r
else
    ip address add $MY_MGMT_IP/24 dev $MY_DEV
    systemctl restart sshd
    sed -i 's/192.168.178.178/10.0.0.71/g' /etc/apt/sources.list
    apt -y update
fi
