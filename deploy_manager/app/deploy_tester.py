import falcon
import os
import sys
from oslo_log import log
from deploy_manager.models.manager import DBManager
from deploy_manager.utils import simport
from deploy_manager.resources import health
from deploy_manager import config
from deploy_manager.driver import loader

import pdb

LOG = log.getLogger(__name__)
CONF = config.CONF

def run_test(config_file=None):
    config_file = ['/etc/deploy_manager/deploy_manager.ini',
                   '/etc/deploy_manager/backends/ip_manager.ini'
                   ]
    #if config_file is None:
    #    config_file = '/etc/deploy_manager/deploy_manager.ini'

    log.register_options(CONF)
    config.init(config_file = config_file)
    pdb.set_trace()
    loader.setup(CONF)

    log.setup(CONF, 'test1')

    from deploy_manager.backends.manager import BackendManager
    m = BackendManager()
    # -------- Use Firewall -------------------------------------------------
    # m.use_firewall(index=1)
    # m.call_firewall(method='info')

if __name__ == '__main__':
    run_test()
