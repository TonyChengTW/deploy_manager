from oslo_config import cfg

CONF = cfg.CONF

default_opts = [
    cfg.StrOpt('name',
                default='deploy_manager',
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
    cfg.StrOpt('database_name', default='deploy_manager',
               help='Used database name'),
    ]

dispatcher_opts = [
    cfg.StrOpt('status',
               default='deploy_manager.resources.status:HealthResource',
               help='HealthResource controller')
    #cfg.StrOpt('ip_changer',
    #           default='deploy_manager.resources.firewall:FirewallAddressResource',
    #           help='FirewallAddressResource controller'),
    #cfg.StrOpt('firewall_device',
    #           default='deploy_manager.resources.firewall:FirewallDeviceResource',
    #           help='FirewallDeviceResource controller'),
]

backends_opts = [
    cfg.StrOpt('ip_manager_driver', default='ipv4', help='The ipv4 plugin will use'),
    cfg.StrOpt('hostname_manager_driver', default='hostname', help='The hostname plugin will use'),
    cfg.StrOpt('upgrade_manager_driver', default='apt_package', help='The apt upgrade plugin will use'),
]

def init(args=None, config_file=None):
    cfg.CONF(args=args,
         project='DEPLOY_MANAGER',
         version="1.0",
         default_config_files=config_file,
         description='Deploy Server RESTful API')

    cfg.CONF.register_opts(default_opts)
    cfg.CONF.register_opts(database_opts, group='database')
    cfg.CONF.register_opts(dispatcher_opts, group='dispatcher')
    cfg.CONF.register_opts(backends_opts, group='backends')
