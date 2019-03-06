import re
import urllib3
import socket
from socket import error as socket_error
from ast import literal_eval

import requests
from netmiko import Netmiko
from oslo_config import cfg
from oslo_log import log
from deploy_manager.models.manager import DBManager
from ip_manager_v1.cache import Cache

LOG = log.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from oslo_config import cfg

#cfg.CONF(args=None,
#         project='IP_MANAGER',
#         version="1.0",
#         default_config_files=['/etc/deploy_manager/backends/ip_manager.ini'],
#         description='Deploy env changer')
#
#conf=cfg.CONF

class Driver(object):

    def __init__(self, conf):
        self._load_conf(conf)


    def _load_conf(self, conf):
        # Load sdnms_api.ini to fetch database options
        #self.db_address = conf.database.address
        #self.db_port = conf.database.port
        #self.db_username = conf.database.username
        #self.db_password = conf.database.password#
        #self.db_name = conf.database.database_name

        # Load fw_fortinet.ini to fetch firewall options
        ip_manager_opts = [
            cfg.StrOpt('hosts',
                       help='node list'),
            ]
        conf.register_opts(ip_manager_opts, group='identities')
        identities_hosts_str = conf.identities.hosts
        hosts = [x for x in identities_hosts_str.split(',')]
        self.fw_identities = hosts

