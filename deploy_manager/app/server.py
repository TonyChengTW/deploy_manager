# Copyright 2019 104 Job Bank Inc. All rights reserved
# Version: 0.1
# tony.cheng@104.com.tw

import falcon
import os
import sys

from oslo_log import log
#from deploy_manager.models.manager import DBManager
from deploy_manager.utils import simport
from deploy_manager.resources import status
from deploy_manager.resources import firewall
from deploy_manager import config
from deploy_manager.driver import loader
from deploy_manager.backends.manager import BackendManager
import pdb


LOG = log.getLogger(__name__)
CONF = config.CONF


def launch(config_file=None):
    if config_file is None:
        config_file = ['/etc/deploy_manager/deploy_manager.ini',
                       '/etc/deploy_manager/backends/ip_manager.ini'
                       ]

    log.register_options(CONF)
    log.setup(CONF, "deploy_manager")

    config.init(config_file=config_file)
    loader.setup(CONF)

    LOG.info('Creating falcon API ...')

    #db = "mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
    #        CONF.database.username, CONF.database.password,
    #        CONF.database.address, CONF.database.port, CONF.database.database_name)
    #mgr = DBManager(db)
    #mgr.setup()

    app = falcon.API()
    status = simport.load(CONF.dispatcher.status)()
    app.add_route("/status", status)

    #pdb.set_trace()
    ip_mapper = BackendManager()
    app.add_route("/ip_mapper", ip_mapper)

    LOG.info('Drivers have been added to the routes!')
    return app

def get_wsgi_app(config_base_path=None, **kwargs):
    return launch()

if __name__ == '__main__':
    from wsgiref import simple_server
    httpd = simple_server.make_server('127.0.0.1', 7878, get_wsgi_app())
    LOG.info('Starting server %s at %s:%s',httpd,'127.0.0.1',7878)
    httpd.serve_forever()
