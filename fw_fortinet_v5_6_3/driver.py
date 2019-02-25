import re
import urllib3
import socket
from socket import error as socket_error
from ast import literal_eval

import requests
from netmiko import Netmiko
from oslo_config import cfg
from oslo_log import log
from sdnms_api.models.manager import DBManager
from fw_fortinet_v5_6_3.cache import Cache

LOG = log.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Driver(object):

    def __init__(self, conf):
        self.fw_identities = self.identity = self.baseurl = \
            self.cmdburl = self.vdom = self.namespace = ''
        self._header = self._headers = self._params = {}
        self.index = int('0')
        self.cookies = {}
        self.access_token = self.http_scheme = self.http_host = self.http_port = self.http_account = \
            self.http_password = self.ssh_host = self.ssh_port = self.ssh_account = \
            self.ssh_password = ''
        self.cache = self.cache_conn = None

        """ Load ini config from CLI parameters """
        self._load_conf(conf)
        self.conf = conf

        """ Create Tables """
        # self._create_orm()

    def _create_orm(self):
        connection = "mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
            self.db_username, self.db_password,
            self.db_address, self.db_port, self.db_name)
        dbmgr = DBManager(connection)
        dbmgr.setup()

    def _load_conf(self, conf):
        # Load sdnms_api.ini to fetch database options
        self.db_address = conf.database.address
        self.db_port = conf.database.port
        self.db_username = conf.database.username
        self.db_password = conf.database.password
        self.db_name = conf.database.database_name

        # Load fw_fortinet.ini to fetch firewall options
        fwid_opts = [
            cfg.StrOpt('fw',
                       help='firewalls list'),
            ]
        conf.register_opts(fwid_opts, group='identities')
        fw_identities_str = conf.identities.fw
        fw_identities = [x for x in fw_identities_str.split(',')]
        self.fw_identities = fw_identities

        ftg_opts = [
            cfg.StrOpt('access_token',
                       default='',
                       help='restful api for restful api'),
            cfg.StrOpt('http_scheme',
                       help='http or https protocol for restful api'),
            cfg.StrOpt('http_host',
                       help='backend IP which provides restful api endpoint'),
            cfg.PortOpt('http_port',
                        default=443,
                        help='The backend port where listen on'),
            cfg.StrOpt('http_account',
                       help='The backend restful api login account'),
            cfg.StrOpt('http_password',
                       help='The backend password for restful api login'),
            cfg.StrOpt('ssh_host',
                       help='backend IP which provides CLI endpoint'),
            cfg.PortOpt('ssh_port',
                        default=22,
                        help='The backend port where ssh listen on'),
            cfg.StrOpt('ssh_account',
                       help='The backend ssh login account'),
            cfg.StrOpt('ssh_password',
                       help='The backend password for ssh login'),
        ]

        for group_name in self.fw_identities:
            conf.register_opts(ftg_opts, group=group_name)

    def _login(self):
        LOG.debug("This is '_login' method")
        payload_login = {"username": self.http_account,
                         "secretkey": self.http_password,
                         "ajax": 1}
        LOG.info("Auth account and password via logincheck api....")
        endpoint = self.baseurl + '/logincheck'

        try:
            resp = requests.post(endpoint,
                                 verify=False,
                                 data=payload_login)
            if resp.status_code != requests.codes.ok:
                LOG.error("Error: API: /logincheck status code is not 200")
            else:
                self.cookies = resp.cookies
                LOG.info("Auth account and password successed!")
            return requests.codes.ok
        except socket.error, msg:
            LOG.error("Could not connect with the firewall: %s\n terminating program" % msg)
        except OSError:
            LOG.error("Connection refused: %s\n , terminating program" % socket_error)

    def logout(self):
        LOG.debug("This is 'logout' method")
        endpoint = self.baseurl + '/logout'
        resp = requests.post(endpoint,
                             verify=False,
                             headers=self._headers)
        resp.cookies.clear()
        LOG.debug("Log-out and clear cookies : %s" % resp.text)
        # self.net_connect.disconnect()
        LOG.debug("Disconnect SSH CLI")
        return requests.codes.ok

    def _add_csrftoken(self):
        LOG.debug("This is '_add_csrftoken' method")
        self._header['X-CSRFTOKEN'] = self.cookies['ccsrftoken'].replace("\"", "")
        self._headers = {"X-CSRFTOKEN": self._header['X-CSRFTOKEN']}

        self._params = {"global": 0,
                        "access_token": self.access_token}

        LOG.info("FortiOS API key is ready to use")

    def _init_ftg(self):
        ftg = {'host': self.ssh_host,
               'port': self.ssh_port,
               'username': self.ssh_account,
               'password': self.ssh_password,
               'device_type': 'fortinet',
               'verbose': False}
        self.net_connect = Netmiko(**ftg)
        self._disable_paging()

    def _disable_paging(self):
        disable_paging_commands = [
            "config global",
            "config system console",
            "set output standard",
            "end\nend"
        ]
        for command in disable_paging_commands:
            self.net_connect.send_command_timing(command)

    def use(self, index=None, identity=None):
        LOG.debug("This is 'use' method")

        self.index = index
        self.identity = identity

        if self.index is None and self.identity is None:
            LOG.error("You need to specify index or identity to use firewall!")
            raise ValueError

        if self.identity is None:
            self.access_token = self.conf.get(self.fw_identities[self.index]).access_token
            self.http_scheme = self.conf.get(self.fw_identities[self.index]).http_scheme
            self.http_host = self.conf.get(self.fw_identities[self.index]).http_host
            self.http_port = self.conf.get(self.fw_identities[self.index]).http_port
            self.http_account = self.conf.get(self.fw_identities[self.index]).http_account
            self.http_password = self.conf.get(self.fw_identities[self.index]).http_password
            self.ssh_host = self.conf.get(self.fw_identities[self.index]).ssh_host
            self.ssh_port = self.conf.get(self.fw_identities[self.index]).ssh_port
            self.ssh_account = self.conf.get(self.fw_identities[self.index]).ssh_account
            self.ssh_password = self.conf.get(self.fw_identities[self.index]).ssh_password
        else:
            self.access_token = self.conf.get(self.identity).access_token
            self.http_scheme = self.conf.get(self.identity).http_scheme
            self.http_host = self.conf.get(self.identity).http_host
            self.http_port = self.conf.get(self.identity).http_port
            self.http_account = self.conf.get(self.identity).http_account
            self.http_password = self.conf.get(self.identity).http_password
            self.ssh_host = self.conf.get(self.identity).ssh_host
            self.ssh_port = self.conf.get(self.identity).ssh_port
            self.ssh_account = self.conf.get(self.identity).ssh_account
            self.ssh_password = self.conf.get(self.identity).ssh_password

        self.baseurl = "%s://%s:%s" % (self.http_scheme, self.http_host, self.http_port)
        self.cmdburl = '/api/v2/cmdb/'

        # Begin to init all procedures
        self._login()
        self._add_csrftoken()
        self._init_ftg()
        self.preload_cache()

    def preload_cache(self):
        LOG.info("Loading firewall data into cache....")
        # get & write firewall's records into Redis
        try:
            # cache vdoms
            self.cache = Cache()
            self.cache_conn = self.cache.create_redis_connection()
            self.cache_conn.flushdb()

            vdoms = self.get_vdom_without_print()

            for vdom in vdoms:
                namespace = self.http_host + "-" + \
                                 'vdoms' + "-" + vdom
                value_vdom = {"name": vdom}
                self.cache.set_cache(namespace=namespace, value=value_vdom)

                # cache addresses
                content = self.get_addr(vdom=vdom)

                for result in content['results']:
                    namespace = self.http_host + "-" + \
                                     vdom + "-" + \
                                     'addresses' + "-" + \
                                     result['name']
                    key_addr_name = result['name']
                    key_addr_type = result['type']
                    key_addr_startip = result['start-ip']
                    key_addr_endip = result['end-ip']
                    key_addr_subnet = result['subnet']
                    key_addr_fqdn = result['fqdn']
                    key_addr_wildcard = result['wildcard']
                    key_addr_wildcardfqdn = result['wildcard-fqdn']
                    key_addr_comment = result['comment']
                    value_addr = {"name": key_addr_name,
                                  "type": key_addr_type,
                                  "start-ip": key_addr_startip,
                                  "end-ip": key_addr_endip,
                                  "subnet": key_addr_subnet,
                                  "fqdn": key_addr_fqdn,
                                  "wildcard": key_addr_wildcard,
                                  "wildcard-fqdn": key_addr_wildcardfqdn,
                                  "comment": key_addr_comment
                                  }
                    self.cache.set_cache(namespace=namespace, value=value_addr)

                # cache services
                content = self.get_service(vdom=vdom)

                for result in content['results']:
                    namespace = self.http_host + "-" + \
                                     vdom + "-" + \
                                     'services' + "-" + \
                                     result['name']
                    key_service_name = result['name']
                    key_service_category = result['category']
                    key_service_protocol = result['protocol']
                    key_servic_tcpportrangee = result['tcp-portrange']
                    key_service_udpportrange = result['udp-portrange']
                    key_service_sctpportrange = result['sctp-portrange']
                    key_service_iprange = result['iprange']
                    key_service_fqdn = result['fqdn']
                    key_service_icmptype = result['icmptype']
                    key_service_protocolnumber = result['protocol-number']
                    key_service_comment = result['comment']
                    value_service = {"name": key_service_name,
                                     "category": key_service_category,
                                     "protocol": key_service_protocol,
                                     "tcp-portrange": key_servic_tcpportrangee,
                                     "udp-portrange": key_service_udpportrange,
                                     "sctp-portrange": key_service_sctpportrange,
                                     "iprange": key_service_iprange,
                                     "fqdn": key_service_fqdn,
                                     "icmptype": key_service_icmptype,
                                     "protocol-number": key_service_protocolnumber,
                                     "comment": key_service_comment
                                     }
                    self.cache.set_cache(namespace=namespace, value=value_service)

                # cache policies
                content = self.get_policy(vdom=vdom)

                for result in content['results']:
                    namespace = self.http_host + "-" + \
                                     vdom + "-" + \
                                     'policies' + "-" + \
                                     str(result['name'])
                    key_policy_id = result['policyid']
                    key_policy_name = result['name']
                    key_policy_srcintf = result['srcintf']
                    key_policy_dstintf = result['dstintf']
                    key_policy_srcaddr = result['srcaddr']
                    key_policy_dstaddr = result['dstaddr']
                    key_policy_schedule = result['schedule']
                    key_policy_service = result['service']
                    key_policy_action = result['action']
                    key_policy_nat = result['nat']
                    key_policy_status = result['status']
                    key_policy_logtraffic = result['logtraffic']
                    key_policy_comments = result['comments']

                    value_policy = {"policyid": key_policy_id,
                                    "name": key_policy_name,
                                    "srcintf": key_policy_srcintf,
                                    "dstintf": key_policy_dstintf,
                                    "srcaddr": key_policy_srcaddr,
                                    "dstaddr": key_policy_dstaddr,
                                    "schedule": key_policy_schedule,
                                    "service": key_policy_service,
                                    "action": key_policy_action,
                                    "nat": key_policy_nat,
                                    "status": key_policy_status,
                                    "logtraffic": key_policy_logtraffic,
                                    "comments": key_policy_comments
                                    }
                    self.cache.set_cache(namespace=namespace, value=value_policy)

                # cache vips
                content = self.get_vip(vdom=vdom)

                for result in content['results']:
                    namespace = self.http_host + "-" + \
                                     vdom + "-" + \
                                     'vips' + "-" + \
                                     result['name']
                    key_vip_name = result['name']
                    key_vip_extintf = result['extintf']
                    key_vip_extip = result['extip']
                    key_vip_extport = result['extport']
                    key_vip_protocol = result['protocol']
                    key_vip_portforward = result['portforward']
                    key_vip_mappedip = result['mappedip']
                    key_vip_mappedport = result['mappedport']
                    key_vip_type = result['type']
                    key_vip_natsourcevip = result['nat-source-vip']
                    key_vip_portmappingtype = result['portmapping-type']
                    key_vip_comment = result['comment']
                    value_vip = {"name": key_vip_name,
                                 "extintf": key_vip_extintf,
                                 "extip": key_vip_extip,
                                 "extport": key_vip_extport,
                                 "protocol": key_vip_protocol,
                                 "portforward": key_vip_portforward,
                                 "mappedip": key_vip_mappedip,
                                 "mappedport": key_vip_mappedport,
                                 "type": key_vip_type,
                                 "nat-source-vip": key_vip_natsourcevip,
                                 "portmapping-type": key_vip_portmappingtype,
                                 "comment": key_vip_comment
                                 }
                    self.cache.set_cache(namespace=namespace, value=value_vip)

                # cache vipgrp
                content = self.get_vipgrp(vdom=vdom)

                for result in content['results']:
                    namespace = self.http_host + "-" + \
                                vdom + "-" + \
                                'vipgrps' + "-" + \
                                result['name']
                    key_vipgrp_name = result['name']
                    key_vipgrp_interface = result['interface']
                    key_vipgrp_member = result['member']
                    key_vipgrp_comments = result['comments']
                    value_vipgrp = {"name": key_vipgrp_name,
                                    "interface": key_vipgrp_interface,
                                    "member": key_vipgrp_member,
                                    "comments": key_vipgrp_comments
                                    }
                    self.cache.set_cache(namespace=namespace, value=value_vipgrp)
            LOG.info("Load to cache successfully!")
            return 1
        except RuntimeError:
            raise

    def info(self):
        LOG.info("This is 'info' method")

        if self.identity is None:
            print "fw_identities[%s] %s" % (self.index, self.fw_identities[self.index])
            print 'http_host : %s' % self.conf.get(self.fw_identities[self.index]).http_host
        else:
            print "identity : %s" % self.identity
            print 'http_host : %s' % self.conf.get(self.identity).http_host

        command_set = [
            'get system status'
        ]
        for command in command_set:
            output = self.net_connect.send_command_timing(command)
            print("+-----------------------------------------------------+")
            print(output)

        return 1

    def get_vdom(self):
        LOG.info("This is 'get_vdom' method")
        exist_vdoms = self.get_vdom_without_print()

        print("+--------------- Get VDOM -----------------------------------+")
        print("VDOMs:\n-------------------------------------------------------------")
        for exist_vdom in exist_vdoms:
            print exist_vdom
        return exist_vdoms

    def get_vdom_without_print(self):
        exist_vdoms = []
        output = ''
        command_set = [
            'config global',
            'config system vdom-property',
            'show | grep edit',
            'end',
            'end'
        ]
        for command in command_set:
            clioutput = self.net_connect.send_command_timing(command)
            if command == command_set[2]:
                output = clioutput.encode('utf-8')
                if 'Command fail' in output or 'Unknown action' in output:
                    LOG.error("%s" % output)
                    raise RuntimeError

        prog = re.compile('edit \"(.*)\"', re.MULTILINE)

        for result in prog.finditer(output):
            exist_vdoms.append(result.group(1))
        return exist_vdoms

    def add_vdom(self, name):
        LOG.info("This is 'add_vdom' method")

        if name is None:
            LOG.error("you need to provide VDOM name!")
            raise RuntimeError("you need to provide VDOM name")

        namespace = self.http_host + "-" + 'vdoms' + "-" + name
        if self.cache.check_cache(namespace=namespace):
            LOG.error("vdom : '%s' is already exist!!" % name)
            return False
        else:
            sub_command = "edit %s" % name
            command_set = [
                'config vdom',
                sub_command,
                'end'
            ]
            for command in command_set:
                clioutput = self.net_connect.send_command_timing(command)
                if command == command_set[1]:
                    output = clioutput.encode('utf-8')
                    if 'Command fail' in output or 'Unknown action' in output:
                        LOG.error("command: %s , respond: %s" % (command, clioutput))
                        raise RuntimeError
                    print("+-----------------------------------------------------+")
                    print "FTG Console : %s" % output
            value = {'name': name}
            self.cache.set_cache(namespace=namespace, value=value)
            LOG.info("VDOM: %s Created!" % name)
            return True

    def del_vdom(self, name, vdom):
        """Not Implemented"""
        raise NotImplementedError

    def get_addr(self, vdom='root'):
        self.vdom = vdom
        self._params["vdom"] = vdom
        LOG.info("This is 'get_addr' method, vdom=%s" % vdom)
        endpoint = self.baseurl + self.cmdburl + '/firewall/address'
        resp = requests.get(endpoint,
                            params=self._params,
                            verify=False,
                            headers=self._headers)
        if resp.ok:
            try:
                content = literal_eval(resp.text)
                # NOTE(tonycheng): You can use "content['results'][10]" to get value
                return content
            except RuntimeError:
                LOG.error("Unknown error when parsing resp.text")
            finally:
                self.logout()
        else:
            LOG.error("Resp text : %s" % resp.text)
            LOG.error("Resp reason : %s" % resp.reason)
            return resp.ok

    def add_addr(self, payload, vdom='root'):
        LOG.info("This is 'add_addr' method, vdom=%s" % vdom)
        if payload is None:
            LOG.error("Error: you need to provide ip/subnet/fqdn and type "
                      "to add address into firewall!")
        namespace = self.http_host + "-" + vdom + "-" + 'addresses-' + payload['name']
        if self.cache.check_cache(namespace=namespace):
            LOG.error("address : '%s' is already exist!!" % payload['name'])
            return False
        else:
            self._params["vdom"] = vdom
            endpoint = self.baseurl + self.cmdburl + '/firewall/address'
            resp = requests.post(endpoint,
                                 params=self._params,
                                 json=payload,
                                 verify=False,
                                 headers=self._headers)
            if resp.ok:
                self.cache.set_cache(namespace=namespace, value=payload)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False

    def del_addr(self, name, vdom='root'):
        LOG.info("This is 'del_addr' method, vdom=%s" % vdom)
        if name is None:
            LOG.error("you need to provide ip/subnet/fqdn "
                      "to delete address from firewall!")
        namespace = self.http_host + "-" + vdom + "-" + 'addresses-' + name
        if self.cache.check_cache(namespace=namespace):
            self._params["vdom"] = vdom

            endpoint = self.baseurl + self.cmdburl + '/firewall/address/'

            resp = requests.delete(endpoint,
                                   params=self._params,
                                   verify=False,
                                   headers=self._headers)
            if resp.ok:
                self.cache.del_cache(namespace=namespace)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False
        else:
            LOG.error("address : '%s' is not exist!!" % name)
            return False

    def set_addr(self, name, payload, vdom='root'):
        LOG.info("This is set_addr method, vdom=%s" % vdom)

        if name is None or payload is None:
            LOG.error("you need to provide ip/subnet/fqdn and type "
                      "to update address into firewall!")
        namespace_before = self.http_host + "-" + vdom + "-" + 'addresses-' + name
        namespace_after = self.http_host + "-" + vdom + "-" + 'addresses-' + payload['name']
        if self.cache.check_cache(namespace=namespace_before):
            self._params["vdom"] = vdom
            endpoint = self.baseurl + self.cmdburl + '/firewall/address/' + name
            resp = requests.put(endpoint,
                                params=self._params,
                                json=payload,
                                verify=False,
                                headers=self._headers)
            if resp.ok:
                self.cache.del_cache(namespace=namespace_before)
                self.cache.set_cache(namespace=namespace_after, value=payload)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False
        else:
            LOG.error("address : '%s' is not exist!!" % name)
            return False

    def get_vip(self, vdom='root'):
        self._params["vdom"] = vdom
        LOG.info("This is 'get_vip' method, vdom=%s" % vdom)
        endpoint = self.baseurl + self.cmdburl + '/firewall/vip/'
        resp = requests.get(endpoint,
                            params=self._params,
                            verify=False,
                            headers=self._headers)
        if resp.ok:
            try:
                content = literal_eval(resp.text)
                # NOTE(tonycheng): You can use "content['results'][10]" to get value
                return content
            except RuntimeError:
                LOG.error("Unknown error when parsing resp.text")
            finally:
                self.logout()
        else:
            LOG.error("Resp text : %s" % resp.text)
            LOG.error("Resp reason : %s" % resp.reason)
            return resp.ok

    def add_vip(self, payload, vdom='root'):
        LOG.info("This is add_vip method, vdom=%s" % vdom)
        if payload is None:
            LOG.error("you need to provide something "
                      "to add virtual IP into firewall!")
        self._params["vdom"] = vdom
        namespace = self.http_host + "-" + vdom + "-" + 'vips-' + payload['name']
        if self.cache.check_cache(namespace=namespace):
            LOG.error("VIP : '%s' is already exist!!" % payload['name'])
            return False
        else:
            endpoint = self.baseurl + self.cmdburl + '/firewall/vip/'
            resp = requests.post(endpoint,
                                 params=self._params,
                                 json=payload,
                                 verify=False,
                                 headers=self._headers)
            if resp.ok:
                self.cache.set_cache(namespace=namespace, value=payload)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False

    def del_vip(self, name, vdom='root'):
        LOG.info("This is 'del_vip' method, vdom=%s" % vdom)
        if name is None:
            LOG.error("you need to VIP name \
                   to delete virtual ip from firewall!")
        namespace = self.http_host + "-" + vdom + "-" + 'vips-' + name
        if self.cache.check_cache(namespace=namespace):
            self._params["vdom"] = vdom

            endpoint = self.baseurl + self.cmdburl + '/firewall/vip/' + name

            resp = requests.delete(endpoint,
                                   params=self._params,
                                   verify=False,
                                   headers=self._headers)
            if resp.ok:
                self.cache.del_cache(namespace=namespace)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False
        else:
            LOG.error("vip : '%s' is not exist!!" % name)
            return False

    def set_vip(self, name, payload, vdom='root'):
        LOG.info("This is 'set_vip' method, vdom=%s" % vdom)

        if payload is None or name is None:
            LOG.error("you need to provide something \
                   to update virtual IP into firewall!")
        namespace_before = self.http_host + "-" + vdom + "-" + 'vips-' + name
        namespace_after = self.http_host + "-" + vdom + "-" + 'vips-' + payload['name']
        if self.cache.check_cache(namespace=namespace_before):
            self._params["vdom"] = vdom
            endpoint = self.baseurl + self.cmdburl + '/firewall/vip/' + name
            resp = requests.put(endpoint,
                                params=self._params,
                                json=payload,
                                verify=False,
                                headers=self._headers)
            if resp.ok:
                self.cache.del_cache(namespace=namespace_before)
                self.cache.set_cache(namespace=namespace_after, value=payload)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False
        else:
            LOG.error("vip : '%s' is not exist!!" % name)
            return False

    def get_policy(self, vdom='root'):
        self._params["vdom"] = vdom
        LOG.info("This is 'get_policy' method, vdom=%s" % vdom)
        endpoint = self.baseurl + self.cmdburl + '/firewall/policy/'
        resp = requests.get(endpoint,
                            params=self._params,
                            verify=False,
                            headers=self._headers)
        if resp.ok:
            try:
                # session = dbmgr.session()
                content = literal_eval(resp.text)

                # NOTE(tonycheng): You can use "content['results'][10]" to get value
                return content
            except RuntimeError:
                LOG.error("Unknown error when parsing resp.text")
            finally:
                self.logout()
        else:
            LOG.error("Resp text : %s" % resp.text)
            LOG.error("Resp reason : %s" % resp.reason)
            return resp.ok

    def add_policy(self, payload, vdom='root'):
        LOG.info("This is add_policy method, vdom=%s" % vdom)
        if payload is None:
            LOG.error("you need to provide something "
                      "to add policy into firewall!")
        namespace = self.http_host + "-" + vdom + "-" + 'policies-' + payload['name']
        if self.cache.check_cache(namespace=namespace):
            LOG.error("policy : '%s' is already exist!!" % payload['name'])
            return False
        else:
            self._params["vdom"] = vdom
            endpoint = self.baseurl + self.cmdburl + '/firewall/policy/'
            resp = requests.post(endpoint,
                                 params=self._params,
                                 json=payload,
                                 verify=False,
                                 headers=self._headers)
            if resp.ok:
                mkey_value = {'mkey': literal_eval(resp.text)['mkey']}
                self.cache.set_cache(namespace=namespace, value=payload)
                self.cache.set_cache(namespace=namespace, value=mkey_value)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False

    def del_policy(self, name, vdom='root'):
        LOG.info("This is 'del_policy' method, vdom=%s" % vdom)
        if name is None:
            LOG.error("you need to provide policy name to delete policy from firewall!")

        namespace = self.http_host + "-" + vdom + "-" + 'policies-' + name
        if self.cache.check_cache(namespace=namespace):
            self._params["vdom"] = vdom
            mkey = str(self.cache.get_cache(namespace=namespace, key='policyid'))
            endpoint = self.baseurl + self.cmdburl + '/firewall/policy/' + mkey

            resp = requests.delete(endpoint,
                                   params=self._params,
                                   verify=False,
                                   headers=self._headers)
            if resp.ok:
                self.cache.del_cache(namespace=namespace)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False
        else:
            LOG.error("policy : '%s' is not exist!!" % name)
            return False

    def set_policy(self, name, payload, vdom='root'):
        LOG.info("This is set_policy method, vdom=%s" % vdom)

        if payload is None or name is None:
            LOG.error("you need to provide something \
                   to update policy into firewall!")
        namespace_before = self.http_host + "-" + vdom + "-" + 'policies-' + name
        namespace_after = self.http_host + "-" + vdom + "-" + 'policies-' + payload['name']
        if self.cache.check_cache(namespace=namespace_before):
            mkey = str(self.cache.get_cache(namespace=namespace_before, key='policyid'))
            self._params["vdom"] = vdom
            endpoint = self.baseurl + self.cmdburl + '/firewall/policy/' + mkey
            resp = requests.put(endpoint,
                                params=self._params,
                                json=payload,
                                verify=False,
                                headers=self._headers)
            if resp.ok:
                self.cache.del_cache(namespace=namespace_before)
                self.cache.set_cache(namespace=namespace_after, value=payload)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False
        else:
            LOG.error("policy : '%s' is not exist!!" % name)
            return False

    def get_service(self, vdom='root'):
        self._params["vdom"] = vdom
        LOG.info("This is 'get_service' method, vdom=%s" % vdom)
        endpoint = self.baseurl + self.cmdburl + '/firewall.service/custom/'
        resp = requests.get(endpoint,
                            params=self._params,
                            verify=False,
                            headers=self._headers)
        if resp.ok:
            try:
                content = literal_eval(resp.text)
                # NOTE(tonycheng): You can use "content['results'][10]" to get value
                return content
            except RuntimeError:
                LOG.error("Unknown error when parsing resp.text")
            finally:
                self.logout()
        else:
            LOG.error("Resp text : %s" % resp.text)
            LOG.error("Resp reason : %s" % resp.reason)
            return resp.ok

    def add_service(self, payload, vdom='root'):
        LOG.info("This is 'add_service' method, vdom=%s" % vdom)
        if payload is None:
            LOG.error("you need to provide something "
                      "to add service into firewall!")
        namespace = self.http_host + "-" + vdom + "-" + 'services-' + payload['name']
        if self.cache.check_cache(namespace=namespace):
            LOG.error("service : '%s' is already exist!!" % payload['name'])
            return False
        else:
            self._params["vdom"] = vdom
            endpoint = self.baseurl + self.cmdburl + '/firewall.service/custom/'
            resp = requests.post(endpoint,
                                 params=self._params,
                                 json=payload,
                                 verify=False,
                                 headers=self._headers)
            if resp.ok:
                self.cache.set_cache(namespace=namespace, value=payload)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False

    def del_service(self, name, vdom='root'):
        LOG.info("This is 'del_service' method, vdom=%s" % vdom)
        if name is None:
            LOG.error("you need to provide service name \
                   to delete service from firewall!")
        self._params["vdom"] = vdom
        namespace = self.http_host + "-" + vdom + "-" + 'services-' + name
        if self.cache.check_cache(namespace=namespace):
            endpoint = self.baseurl + self.cmdburl + '/firewall.service/custom/' + name
            resp = requests.delete(endpoint,
                                   params=self._params,
                                   verify=False,
                                   headers=self._headers)
            if resp.ok:
                self.cache.del_cache(namespace=namespace)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False
        else:
            LOG.error("service : '%s' is not exist!!" % name)
            return False

    def set_service(self, name, payload, vdom='root'):
        LOG.info("This is 'set_service' method, vdom=%s" % vdom)
        if payload is None or name is None:
            LOG.error("you need to provide something \
                   to update service into firewall!")
        namespace_before = self.http_host + "-" + vdom + "-" + 'services-' + name
        namespace_after = self.http_host + "-" + vdom + "-" + 'services-' + payload['name']
        if self.cache.check_cache(namespace=namespace_before):
            self._params["vdom"] = vdom
            endpoint = self.baseurl + self.cmdburl + '/firewall.service/custom/' + name
            resp = requests.put(endpoint,
                                params=self._params,
                                json=payload,
                                verify=False,
                                headers=self._headers)
            if resp.ok:
                self.cache.del_cache(namespace=namespace_before)
                self.cache.set_cache(namespace=namespace_after, value=payload)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False
        else:
            LOG.error("service : '%s' is not exist!!" % name)
            return False

    def get_vipgrp(self, vdom='root'):
        self._params["vdom"] = vdom
        LOG.info("This is 'get_vipgrp' method, vdom=%s" % vdom)
        endpoint = self.baseurl + self.cmdburl + '/firewall/vipgrp'
        resp = requests.get(endpoint,
                            params=self._params,
                            verify=False,
                            headers=self._headers)
        if resp.ok:
            try:
                content = literal_eval(resp.text)
                # NOTE(tonycheng): You can use "content['results'][10]" to get value
                return content
            except RuntimeError:
                LOG.error("Unknown error when parsing resp.text")
            finally:
                self.logout()
        else:
            LOG.error("Resp text : %s" % resp.text)
            LOG.error("Resp reason : %s" % resp.reason)
            return resp.ok

    def add_vipgrp(self, payload, vdom='root'):
        LOG.info("This is 'add_vipgrp' method, vdom=%s" % vdom)
        namespace = self.http_host + "-" + vdom + "-" + 'vipgrps-' + payload['name']
        if self.cache.check_cache(namespace=namespace):
            LOG.error("vip group : '%s' is already exist!!" % payload['name'])
            return False
        else:
            if payload is None:
                LOG.error("you need to provide something "
                          "to add vip group into firewall!")
            self._params["vdom"] = vdom
            endpoint = self.baseurl + self.cmdburl + '/firewall/vipgrp/'
            resp = requests.post(endpoint,
                                 params=self._params,
                                 json=payload,
                                 verify=False,
                                 headers=self._headers)
            if resp.ok:
                self.cache.set_cache(namespace=namespace, value=payload)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False

    def del_vipgrp(self, name, vdom='root'):
        LOG.info("This is 'del_vipgrp' method, vdom=%s" % vdom)
        if name is None:
            LOG.error("you need to provide vipgrp name \
                   to delete service from firewall!")
        namespace = self.http_host + "-" + vdom + "-" + 'vipgrps-' + name
        if self.cache.check_cache(namespace=namespace):
            self._params["vdom"] = vdom
            endpoint = self.baseurl + self.cmdburl + '/firewall/vipgrp/' + name
            resp = requests.delete(endpoint,
                                   params=self._params,
                                   verify=False,
                                   headers=self._headers)
            if resp.ok:
                self.cache.del_cache(namespace=namespace)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False

    def set_vipgrp(self, name, payload, vdom='root'):
        LOG.info("This is 'set_vipgrp' method, vdom=%s" % vdom)
        if payload is None or name is None:
            LOG.error("you need to provide something \
                   to update vip group into firewall!")
        namespace_before = self.http_host + "-" + vdom + "-" + 'vipgrps-' + name
        namespace_after = self.http_host + "-" + vdom + "-" + 'vipgrps-' + payload['name']
        if self.cache.check_cache(namespace=namespace_before):
            self._params["vdom"] = vdom
            endpoint = self.baseurl + self.cmdburl + '/firewall/vipgrp/' + name
            resp = requests.put(endpoint,
                                params=self._params,
                                json=payload,
                                verify=False,
                                headers=self._headers)
            if resp.ok:
                self.cache.del_cache(namespace=namespace_before)
                self.cache.set_cache(namespace=namespace_after, value=payload)
                LOG.info("Resp text is : %s" % resp.text)
                return True
            else:
                LOG.error("Return Code is : %s" % resp.status_code)
                LOG.error("Resp text is : %s" % resp.text)
                LOG.error("Resp reason is : %s" % resp.reason)
                return False
        else:
            LOG.error("VIP group : '%s' is not exist!!" % name)
            return False

    def save_config(self, vdom='root'):
        """Not Implemented"""
        raise NotImplementedError
