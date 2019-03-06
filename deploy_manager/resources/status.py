import falcon

class HealthResource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ('{"result":"OK"}')
