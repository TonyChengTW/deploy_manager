import falcon
import urllib3
from netmiko import Netmiko
from oslo_log import log
from oslo_config import cfg
import json

import pdb

LOG = log.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Driver(object):

    def __init__(self, conf):
        self._load_conf(conf)

    def _load_conf(self, conf):
        identities_opts = [
            cfg.StrOpt('hosts',
                       help='node list'),
            ]

        nodes_opts = [
            cfg.StrOpt('ip', default='0.0.0.0', help='aaa'),
            cfg.StrOpt('mac', default='00:00:00:00:00:00', help='bbb'),
            cfg.StrOpt('ssh_port', default='22', help='ccc'),
            cfg.StrOpt('ssh_account', default='root', help='ddd'),
            cfg.StrOpt('ssh_password', default='password', help='eee')
            ]

        conf.register_opts(identities_opts, group='identities')
        conf.register_opts(nodes_opts, group='node1')

        identities_hosts_str = conf.identities.hosts
        hosts = [x for x in identities_hosts_str.split(',')]
        self.hosts = hosts

        self.myip = conf.node1.ip

    def on_get_ipmac(self, req, resp, **kwargs):
        #pdb.set_trace()
        try:
            if True:
                jsonbody = 'myip = ' + self.myip
                resp.body = json.dumps(jsonbody)
                resp.status = falcon.HTTP_200
        except:
            resp.status = falcon.HTTP_404
        finally:
            return resp