# Copyright 2019 104 Job Bank Inc. All rights reserved
# Version: 0.1
# tony.cheng@104.com.tw

from deploy_manager.app import server

application = server.get_wsgi_app()
