# Copyright 2019 104 Job Bank Inc. All rights reserved
# Version: 0.1
# tony.cheng@104.com.tw

from deploy_manager.driver import loader

class BackendManager(object):

    def __init__(self):
        self._ip_manager = loader.ip_manager_driver()

    def on_get(self, req, resp, **kwargs):
        return self._ip_manager.on_get_ipmac(req, resp)
