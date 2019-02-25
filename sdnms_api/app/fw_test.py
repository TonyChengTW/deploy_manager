import falcon
import os
import sys

from oslo_log import log
from sdnms_api.models.manager import DBManager
from sdnms_api.utils import simport
from sdnms_api.resources import health
from sdnms_api.resources import firewall
from sdnms_api import config
from sdnms_api.driver import loader

import pdb

LOG = log.getLogger(__name__)
CONF = config.CONF


def run_test(config_file=None):
#    config_files = ['/home/tony/proj/cc-iaas-sdnms/etc/sdnms_api/sdnms_api.ini',
#                   '/home/tony/proj/cc-iaas-sdnms/etc/sdnms_api/backends/fw_fortinet_v5.6.3.ini'
#                   ]
    if config_file is None:
        config_file = '/etc/sdnms_api/sdnms_api.ini'

    log.register_options(CONF)
    config.init(config_file = config_file)
    # pdb.set_trace()
    loader.setup(CONF)

    log.setup(CONF, 'test1')

    from sdnms_api.backends.manager import BackendManager
    m = BackendManager()
    # -------- Use Firewall -------------------------------------------------
    # m.use_firewall(index=1)
    m.use_firewall(identity='fortivm2')
    # m.use_firewall(identity='fw1')
    # m.use_firewall()

    vdom = 'tony3'

    """
    # m.call_firewall(method='info')

    # -------- Add VDOM ------------------------------------------------------
    name = 'tony3'
    # m.call_firewall(method='add_vdom', name=name)

    # m.call_firewall(method='get_vdom')



    # -------- Get Addr -------------------------------------------------
    # m.call_firewall(method='get_addr', vdom=vdom)

    # -------- Add Addr -------------------------------------------------
    payload = {
              'name': "11.11.11.178",
              'type': "ipmask",
              # 'start-ip': None,
              # 'end-ip': None,
              'subnet': "11.11.11.178 255.255.255.255",
              # 'fqdn': None,
              # 'wildcard': None,
              # 'wildcard-fqdn': None,
              'comment': "test add method"
              }
    m.call_firewall(method='add_addr', vdom=vdom, payload=payload)


    # -------- Del Addr -------------------------------------------------
    name = '11.11.11.178'
    #m.call_firewall(method='del_addr', vdom=vdom, name=name)

    # -------- Set Addr -------------------------------------------------
    name = '11.11.11.178'
    payload = {
        'name': '21.11.11.178',
        'type': "ipmask",
        # 'start-ip': None,
        # 'end-ip': None,
        'subnet': "21.11.11.178 255.255.255.255",
        # 'fqdn': None,
        # 'wildcard': None,
        # 'wildcard-fqdn': None,
        'comment': "test set method"
    }
    m.call_firewall(method='set_addr', vdom=vdom, name=name, payload=payload)


    # ------------  Get VIP -----------------------------------------------
    m.call_firewall(method='get_vip', vdom=vdom)


    # ------------  Add/Set VIP -----------------------------------------------
    name = "test2"
    payload = {
               'name': "test2",
               'extintf': "any",
               'extip': "203.103.103.103",
               'extport': "23",
               'protocol': "telnet",
               'portforward': "enable",
               'mappedip': [{
                            'range': "23.13.13.103"
                            }],
               'mappedport': "23",
               'type': "static-nat",
               'nat-source-vip': "disable",
               'portmapping-type': "1-to-1",
               'comment': "test set method"
              }
    # m.call_firewall(method='add_vip', vdom=vdom, payload=payload)

    # m.call_firewall(method='set_vip', vdom=vdom, payload=payload, name=name)

    name = 'test2'
    m.call_firewall(method='del_vip', vdom=vdom, name=name)
    
    #m.call_firewall(method='get_vipgrp', vdom=vdom)
    m.call_firewall(method='logout')
   """
    # ------------  Get Policy -----------------------------------------------
    # m.call_firewall(method='get_policy', vdom=vdom)
    


    # ------------  Add Policy -----------------------------------------------
    vdom = 'tony3'
    payload = {
                'name': 'deny-vm3',
                'srcintf': [{'name': 'port3'}, ],
                'dstintf': [{'name': 'port3'}, ],
                'srcaddr': [{'name': 'all'}, ],
                'dstaddr': [{'name': 'vipgrp3'}, ],
                'schedule': 'always',
                'service': [{'name': 'SSH'}, ],
                'action': 'deny',
                'nat': 'disable',
                'logtraffic': 'all',
                'status': 'enable',
                'comments': 'test set policy via API'
               }
    name = 'deny-vm2'
    m.call_firewall(method='set_policy', name=name, payload=payload, vdom=vdom)
    # m.call_firewall(method='add_policy', payload=payload, vdom=vdom)

    # mkey = '4'


    name = 'deny-vm2'
    # ------------  Delete Policy -----------------------------------------------
    # m.call_firewall(method='del_policy', name=name, vdom=vdom)

    """
    # ------------  Get Service -----------------------------------------------
    # m.call_firewall(method='get_service', vdom=vdom)

    # ------------  Add Service -----------------------------------------------
    vdom = 'tony3'
    payload1 = {'name': 'add service3',
                'category': 'Web Access',  # need specify with a defined category
                'protocol': 'TCP\\/UDP\\/SCTP',  # protocol : 'ICMP' for only icmp
                'tcp-portrange': '80',
                'udp-portrange': '',
                'sctp-portrange': '',
                'iprange': '1.2.3.5',
                'fqdn': '',
                'icmptype': '',
                'protocol-number': 6,     # ICMP=1, TCP=6 , UDP=17 , SCTP=132
                'comment': 'add service'
               }

    payload2 = {'name': 'set service3',
                'category': 'FTP',  # need specify with a defined category
                'protocol': 'TCP\\/UDP\\/SCTP',  # protocol : 'ICMP' for only icmp
                'tcp-portrange': '23',
                'udp-portrange': '',
                'sctp-portrange': '',
                'iprange': '5.6.7.8',
                'fqdn': '',
                'icmptype': '',
                'protocol-number': 6,     # ICMP=1, TCP=6 , UDP=17 , SCTP=132
                'comment': 'add service'
               }

    # m.call_firewall(method='add_service', payload=payload1, vdom=vdom)
    # m.call_firewall(method='add_service', payload=payload2, vdom=vdom)


# ------------  Delete Service -----------------------------------------------
    name = 'set service3'
    vdom = 'tony3'
    m.call_firewall(method='del_service', name=name, vdom=vdom)

# ------------  Set Service -----------------------------------------------
    name = 'add service3'
    vdom = 'tony3'
    payload = {'name': 'set service3',
                'comment': '',
                'protocol': 'TCP\\/UDP\\/SCTP',  # protocol : 'ICMP' for only icmp
                'iprange': '5.6.7.8',
                'category': '',  # need specify with a defined category, a null value will be 'Uncategorized' cat.
                'protocol-number': 17,  # ICMP=1, TCP=6 , UDP=17 , SCTP=132
                # 'tcp-portrange': '80',
                'udp-portrange': '3390'
                }
    # m.call_firewall(method='set_service', name=name, payload=payload, vdom=vdom)

# ----------------- Get VIP Group ----------------------------------------------------------
    vdom = 'tony3'

    # m.call_firewall(method='get_vipgrp', vdom=vdom)

# ----------------- Add/Set VIP Group ----------------------------------------------------------
    name = 'vipgrp1-add'
    payload = {'name': 'vipgrp3',
               'interface': 'any',
               'member': [
                   # {'name': 'vm1-icmp'},
                   # {'name': 'vm2-http'},
                   # {'name': 'vm2-ssh'},
                   {'name': 'vip1'},
                   {'name': 'vip3'},
               ],
               'comments': 'test'
               }
    # m.call_firewall(method='add_vipgrp', payload=payload, vdom=vdom)
    # m.call_firewall(method='set_vipgrp', name=name, payload=payload, vdom=vdom)
    m.call_firewall(method='del_vipgrp', name=name, vdom=vdom)
    """
if __name__ == '__main__':
    run_test()
