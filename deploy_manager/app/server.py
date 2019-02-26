import falcon
import os
import sys

from oslo_log import log
from deploy_manager.models.manager import DBManager
from deploy_manager.utils import simport
from deploy_manager.resources import health
from deploy_manager.resources import firewall
from deploy_manager import config
from deploy_manager.driver import loader

LOG = log.getLogger(__name__)
CONF = config.CONF


def launch(config_file=None):
    if config_file is None:
        config_file = '/etc/deploy_manager/deploy_manager.ini'

    log.register_options(CONF)
    log.setup(CONF, "deploy_manager")

    config.init(config_file=config_file)
    loader.setup(CONF)

    LOG.info('Creating falcon API ...')
    app = falcon.API()

    db = "mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
            CONF.database.username, CONF.database.password,
            CONF.database.address, CONF.database.port, CONF.database.database_name)
    mgr = DBManager(db)
    mgr.setup()

    app = falcon.API()
    health = simport.load(CONF.dispatcher.health)(mgr)
    app.add_route("/health", health)
    firewall_address = simport.load(CONF.dispatcher.firewall_address)(mgr)
    app.add_route("/firewall/address", firewall_address)

    LOG.info('Dispatcher drivers have been added to the routes!')
    return app

def get_wsgi_app(config_base_path=None, **kwargs):
    return launch()

if __name__ == '__main__':
    from wsgiref import simple_server
    httpd = simple_server.make_server('127.0.0.1', 8000, get_wsgi_app())
    LOG.info('Starting server %s at %s:%s',httpd,'127.0.0.1',8000)
    httpd.serve_forever()
