## Install packages
```
yum install -y epel-release
yum install -y httpd mod_wsgi
yum install -y python-pip gcc python-devel
yum install -y redis
pip install virtualenv
```

## Install MariaDB 10.2
```
cat > /etc/yum.repos.d/MariaDB.repo << EOF
[mariadb]
name = MariaDB
baseurl = http://yum.mariadb.org/10.2/centos7-amd64
gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1
EOF

yum install -y MariaDB-server MariaDB-client
systemctl start mariadb
systemctl enable mariadb
```

Firewall Setting
```
firewall-cmd --permanent --add-service=mysql
firewall-cmd --permanent --add-port=3306/tcp
firewall-cmd --reload
```

## Create project
```
cd /opt
git clone http://172.16.100.91/cc-iaas/cc-iaas-sdnms.git
cd cc-iaas-sdnms
virtualenv python_env
source python_env/bin/activate

pip install -r requirements.txt -c upper-constraints-pike.txt
pip install -r requirements.txt
python setup.py develop
```

### Install Customize module - netmiko (CloudCube version)
```
cd /opt
git clone https://github.com/TonyChengTW/netmiko.git
cd netmiko
git branch checkout v2.1.1-cc-001
cd dist
pip install netmiko-2.1.1-cc.tar.gz
```

## Install backend drivers
```
HOW?
```

## Start dev http server
```
python sdnms_api/app/server.py --config-file etc/sdnms_api/sdnms_api_dev.ini --config-file etc/sdnms_api/backends/fw_fortinet_v5.6.3.ini
```

## Test dev http server
```
curl http://localhost:8000/health
```
