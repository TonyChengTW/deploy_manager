from oslo_log import log
from stevedore import driver

LOG = log.getLogger(__name__)


class DriverLoader(object):
    NAMESPACE_FIREWALL = 'backend.fw.drivers'
    NAMESPACE_WAF = 'backend.waf.drivers'
    NAMESPACE_SWITCH = 'backend.switch.drivers'

    def __init__(self):
        self._drivers = {}
        self._conf = None

    def setup(self, conf):
        LOG.info("setup conf: %s", conf.backends.items())
        self._conf = conf
        if conf.backends.fw_driver:
            driver_name = conf.backends.fw_driver
            driver = self._load_driver(self.NAMESPACE_FIREWALL, driver_name)
            self._drivers['firewall'] = driver
        
        if conf.backends.waf_driver:
            driver_name = conf.backends.waf_driver
            driver = self._load_driver(self.NAMESPACE_WAF, driver_name)
            self._drivers['waf'] = driver
        
        if conf.backends.switch_driver:
            driver_name = conf.backends.switch_driver
            driver = self._load_driver(self.NAMESPACE_SWITCH, driver_name)
            self._drivers['switch'] = driver

    def _load_driver(self, namespace, name, invoke_load=True):
        try:
            LOG.info("Attempting to import driver %s:%s", namespace, name)
            mgr = driver.DriverManager(namespace,
                                       name,
                                       invoke_args=[self._conf],
                                       invoke_on_load=invoke_load)
            return mgr.driver
        except RuntimeError as e:
            LOG.warning("Failed to load driver from %s, %s" % (__file__, e))
#        except TypeError as e:
#            LOG.warning("Failed to load driver from %s, %s" % (__file__, e))
#        except:
#            LOG.warning("Failed to load driver %s:%s" % (namespace, name))

    def get_driver(self, driver_name):
        try:
            return self._drivers[driver_name]
        except KeyError:
            return None

    def firewall_driver(self):
        return self.get_driver('firewall')

    def waf_driver(self):
        return self.get_driver('waf')

    def switch_driver(self):
        return self.get_driver('switch')

loader = DriverLoader()
