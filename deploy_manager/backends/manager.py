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

class SampleWaf(object):
    def use(self, index, identity):
        self._index = index
        self._identity = identity
    def info(self):
        print(self._index)
        print(self._identity)

class SampleSwitch(object):
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
        self._firewall = loader.firewall_driver()
        # self._firewall = loader.firewall_driver()(conf)
        self._waf = SampleWaf()
        self._switch = SampleSwitch()

    def use_firewall(self, index=0, identity=None, selector=None):
        if selector is None:
            self._firewall.use(index=index, identity=identity)
        else:
            self._firewall.use(**selector.select())

    def use_waf(self, index=0, identity=None, selector=None):
        if selector is None:
            self._waf.use(index=index, identity=identity)
        else:
            self._waf.use(**selector.select())

    def use_switch(self, index=0, identity=None, selector=None):
        if selector is None:
            self._switch.use(index=index, identity=identity)
        else:
            self._switch.index = selector.get_index()
            self._switch.use(**selector.select())

    def call_firewall(self, method=None, *args, **kwargs):
        fn = getattr(self._firewall, method)
        return fn(*args, **kwargs)

    def call_waf(self, method=None, *args, **kwargs):
        fn = getattr(self._waf, method)
        return fn(*args, **kwargs)

    def call_switch(self, method=None, *args, **kwargs):
        fn = getattr(self._switch, method)
        return fn(*args, **kwargs)
