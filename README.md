# Deploy Manager

## Scope

* Deploy Ubuntu or CentOS Server by PXE and change IP by MAC address.
* Through REST API , at this time, it only support GET method

## Example in server side
```
# cd /deploy_u18
# git clone https://github.com/TonyChengTW/deploy_manager
# virtualenv /deploy_u18/deploy_manager
# source /deploy_u18/deploy_manager/bin/activate
# cd /deploy_u18/deploy_manager
# pip install -r requirement.txt
# python setup.py install
# bin/deploy_manager
```
The deploy_manager daemon written by python can be lauched by systemctl
``` # systemctl start deploy_manager ```

## Configuration Files

`/etc/deploy_manager/backends/ip_manager.ini`
```
[DEFAULT]

[identities]
hosts = ctrl1,comp1,comp2

[ctrl1]
ip = 10.0.0.111
mac = 00:0c:29:c5:a0:0a

[comp1]
ip = 10.0.0.121
mac = 00:0c:29:a8:7c:5c

[comp2]
ip = 10.0.0.122
mac = 00:0c:29:3c:6e:bd
```

## Example in client side
```curl http://[deploy_server]:7878/ip_mapper?mac=00:0c:29:a8:7c:5c```
It will return an IP which is matched an node : 10.0.0.121

You need to filliup both [identities] and [xxx] group options, which xxx is the hostname.

## KickStart configuration
The Kckstart config file is located in
```/deploy_u18/u18.04.1-server-amd64/ks.cfg```
Which defines Ubuntu 18.04.1 install options.

KickStart at %post
- Defines apt/sources.list to the deploy server (inside internal network)
- Change IP by lookup `/etc/deploy_manager/backends/ip_manager.ini` via Deploy Manager API
- add a default ssh key
- Change locale
- rename raw nic device name by generating grub.cfg via grub-mkconfig (editing /etc/default/grub)

## License

MIT / BSD

## Author Information
104 Job Bank Corp.
[tony.cheng@104.com.tw](mailto:tony.cheng@104.com.tw)
