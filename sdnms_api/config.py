from oslo_config import cfg

CONF = cfg.CONF

default_opts = [
    cfg.StrOpt('name',
                default='cc_iaas_sdnms',
                help='Process name.'),
]

database_opts = [
    cfg.StrOpt('address',
                default='127.0.0.1',
                help='Binding address'),
    cfg.IntOpt('port', default=3306,
               help='The database port where listen on'),
    cfg.StrOpt('username', default='root',
               help='The database user of login'),
    cfg.StrOpt('password', default='root',
               help='The database password of login'),
    cfg.StrOpt('database_name', default='sdnms_api',
               help='Used database name'),
    ]

dispatcher_opts = [
    cfg.StrOpt('health',
               default='sdnms_api.resources.health:HealthResource',
               help='HealthResource controller'),
    cfg.StrOpt('firewall_address',
               default='sdnms_api.resources.firewall:FirewallAddressResource',
               help='FirewallAddressResource controller'),
    cfg.StrOpt('firewall_device',
               default='sdnms_api.resources.firewall:FirewallDeviceResource',
               help='FirewallDeviceResource controller'),
]

backends_opts = [
    cfg.StrOpt('fw_driver', default='', help='The firewall plugin will use'),
    cfg.StrOpt('waf_driver', default='', help='The WAF plugin will use'),
    cfg.StrOpt('switch_driver', default='', help='The switch plugin will use'),
]

def init(args=None, config_file=None):
    cfg.CONF(args=args,
         project='SDNMS',
         version="1.0",
         default_config_files=[config_file],
         description='SDNMS RESTful API')

    cfg.CONF.register_opts(default_opts)
    cfg.CONF.register_opts(database_opts, group='database')
    cfg.CONF.register_opts(dispatcher_opts, group='dispatcher')
    cfg.CONF.register_opts(backends_opts, group='backends')
