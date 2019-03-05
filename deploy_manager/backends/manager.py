from deploy_manager.driver import loader

"""
from oslo_config import cfg

import pdb

cfg.CONF(args=None,
         project='DEPLOY_MANAGER',
         version="1.0",
         default_config_files='etc/deploy_manager/backends/ip_manager.ini',
         description='SDNMS Forti')

conf=cfg.CONF
"""
class SampleFirewall(object):
    def use(self, index, identity):
        self._index = index
        self._identity = identity
    def info(self):
        print(self._index)
        print(self._identity)


class BackendManager(object):
    """Sample usage

    from deploy_manager.backends.selector import SampleSelector
    from deploy_manager.backends.manager import BackendManager
    m = BackendManager()
    m.use_firewall()
    m.call_firewall(method='info')

    m.use_firewall(index=1)
    m.call_firewall(method='info')

    m.use_firewall(identity='cisco')
    m.call_firewall(method='info')

    m.use_firewall(selector=SampleSelector())
    m.call_firewall(method='info')
    """
    def __init__(self):
        self._ip_manager = loader.ip_manager_driver()

    def set_ip_by_mac(self, index=0, identity=None, selector=None):
        if selector is None:
            self._firewall.use(index=index, identity=identity)
        else:
            self._firewall.use(**selector.select())
