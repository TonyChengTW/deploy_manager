# Copyright 2019 104 Job Bank Inc. All rights reserved
# Version: 0.1
# tony.cheng@104.com.tw

import falcon
import urllib3
# from netmiko import Netmiko
from oslo_log import log
from oslo_config import cfg
import json

import pdb

LOG = log.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Driver(object):

    def __init__(self, conf):
        self._conf = conf
        self._load_conf()

    def _load_conf(self):
        identities_opts = [
            cfg.StrOpt('hosts',
                       help='node list'),
            ]

        nodes_opts = [
            cfg.StrOpt('ip', default='0.0.0.0', help='aaa'),
            cfg.StrOpt('mac', default='00:00:00:00:00:00', help='bbb'),
            # cfg.StrOpt('ssh_port', default='22', help='ccc'),
            # cfg.StrOpt('ssh_account', default='root', help='ddd'),
            # cfg.StrOpt('ssh_password', default='password', help='eee')
            ]

        self._conf.register_opts(identities_opts, group='identities')
        self._conf.register_opts(nodes_opts, group='node1')

        identities_hosts_str = self._conf.identities.hosts
        self.hosts = [x for x in identities_hosts_str.split(',')]

        self.nodes = {}
        for group_nodes_opts in self.hosts:
            self._conf.register_opts(nodes_opts, group=group_nodes_opts)
            node_value = self._conf.get(group_nodes_opts).mac
            self.nodes[group_nodes_opts] = node_value

    def on_get_ipmac(self, req, resp, **kwargs):
        # pdb.set_trace()
        my_ip = ''
        for node, value in self.nodes.iteritems():
            if req.params['mac'] in value:
                my_ip = self._conf.get(node).ip
                # my_ssh_port = self._conf.get(node).ssh_port
                # my_ssh_account = self._conf.get(node).ssh_account
                # my_ssh_password = self._conf.get(node).ssh_password
                jsonbody = my_ip
                resp.body = json.dumps(jsonbody)
                resp.status = falcon.HTTP_200
                break
        if not my_ip:
            jsonbody = "MAC address not found in ip_manager.ini"
            LOG.warn(jsonbody)
            resp.body = json.dumps(jsonbody)
            resp.status = falcon.HTTP_404
#         return resp
