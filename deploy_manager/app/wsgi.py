from deploy_manager.app import server

application = server.get_wsgi_app()
