from oslo_log import log
from stevedore import driver

LOG = log.getLogger(__name__)


class DriverLoader(object):
    NAMESPACE_IP = 'ip_manager.drivers'
    NAMESPACE_HOSTNAME = 'hostname_manager.drivers'
    NAMESPACE_UPGRADE = 'upgrade_manager.drivers'

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
        
        if conf.backends.hostname_manager_driver:
            driver_name = conf.backends.hostname_manager_driver
            driver = self._load_driver(self.NAMESPACE_HOSTNAME, driver_name)
            self._drivers['hostname_manager'] = driver
        
        if conf.backends.switch_driver:
            driver_name = conf.backends.upgrade_manager_driver
            driver = self._load_driver(self.NAMESPACE_UPGRADE, driver_name)
            self._drivers['upgrade_manager'] = driver

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

    def hostname_manager_driver(self):
        return self.get_driver('hostname_manager')

    def upgrade_manager_driver(self):
        return self.get_driver('upgrade_manager')

loader = DriverLoader()
