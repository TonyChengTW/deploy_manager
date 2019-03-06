from oslo_log import log
from stevedore import driver

LOG = log.getLogger(__name__)


class DriverLoader(object):
    NAMESPACE_IP = 'backend.ip.drivers'

    def __init__(self):
        self._drivers = {}
        self._conf = None

    def setup(self, conf):
        LOG.info("setup conf: %s", conf.backends.items())
        self._conf = conf
        if conf.backends.ip_manager_driver:
            driver_name = conf.backends.ip_manager_driver
            driver = self._load_driver(self.NAMESPACE_IP, driver_name)
            self._drivers['ip_manager'] = driver
        
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

    def ip_manager_driver(self):
        return self.get_driver('ip_manager')

loader = DriverLoader()
