import falcon

from deploy_manager.resources.base_resource import BaseResource

class HealthResource(BaseResource):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ('{"result":"OK"}')
