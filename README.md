# Scope

* Deploy Ubuntu or CentOS Server by PXE and change IP by MAC address.
* Through REST API , at the time, it only support GET method

# Example in server side
cd ~
git clone REPO
virtualenv ~/deploy_manager
source ~/deploy_manager/bin/activate
cd ~/deploy_manager
pip install -r requirement.txt
python setup.py install
bin/deploy_manager

# Example in client side
curl http://[deploy_server]:7878/ip_mapper?mac=00:11:22:33:44:55

# Kick Start at %post


Author: tony.cheng@104.com.tw
