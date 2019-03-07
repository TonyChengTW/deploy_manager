from deploy_manager.driver import loader

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

    def on_get(self, req, resp, **kwargs):
        return self._ip_manager.on_get_ipmac(req, resp)
