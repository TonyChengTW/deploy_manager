import falcon

from falcon.media.validators.jsonschema import validate

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from sdnms_api.models.firewall import FirewallAddressModel
from sdnms_api.resources.base_resource import BaseResource
from sdnms_api.medium import load_schema


class FirewallAddressResource(BaseResource):

    def on_get(self, req, resp):
        model_list = FirewallAddressModel.get_list(self.db.session)

        address = [model.as_dict for model in model_list]
        resp.status = falcon.HTTP_200
        # resp.append_header("CC_ERROR_MSG", "test")
        resp.media = address

    @validate(load_schema('firewall_address_creation'))
    def on_post(self, req, resp):

        # todo: max_port load from backend ini config file
        max_port = 10
        model = FirewallAddressModel(
                name=req.media.get('name'),
                type=req.media.get('type'),
                content=req.media.get('content'),
                interface=req.media.get('interface'),
                comment=req.media.get('comment')
        )

        try:
            if req.media.get('interface') > max_port:
                raise ValueError("Interface value error", 'Could not over to max ports')

            model.save(self.db.session)
        except ValueError as error:
            raise falcon.HTTPBadRequest(
                    error.args[0],
                    error.args[1]
            )
        except IntegrityError:
            raise falcon.HTTPBadRequest(
                    'Name exists',
                    'Could not create firewall address due to name already existing'
            )

        resp.status = falcon.HTTP_201
        resp.media = {
            'id': model.id
        }

    def on_delete(self, req, resp):
        try:
            if req.media.get('id') <= 0:
                raise ValueError("ID value error", 'Must have id')
            else:
                model = FirewallAddressModel.get(self.db.session, req.media.get('id'))
                model.delete(self.db.session)
        except ValueError as error:
            raise falcon.HTTPBadRequest(
                    error.args[0],
                    error.args[1]
            )
        except NoResultFound:
            raise falcon.HTTPBadRequest(
                    'Firewall Address not exist',
                    'Item is not exist, check your ID input'
            )

        resp.status = falcon.HTTP_200
        resp.media = "OK"


class FirewallServiceResource(BaseResource):

    def on_get(self, req, resp):
        model_list = FirewallAddressModel.get_list(self.db.session)

        address = [model.as_dict for model in model_list]
        resp.status = falcon.HTTP_200
        # resp.append_header("CC_ERROR_MSG", "test")
        resp.media = address

    @validate(load_schema('firewall_address_creation'))
    def on_post(self, req, resp):

        # todo: max_port load from backend ini config file
        max_port = 10
        model = FirewallAddressModel(
                name=req.media.get('name'),
                type=req.media.get('type'),
                content=req.media.get('content'),
                interface=req.media.get('interface'),
                comment=req.media.get('comment')
        )

        try:
            if req.media.get('interface') > max_port:
                raise ValueError("Interface value error", 'Could not over to max ports')

            model.save(self.db.session)
        except ValueError as error:
            raise falcon.HTTPBadRequest(
                    error.args[0],
                    error.args[1]
            )
        except IntegrityError:
            raise falcon.HTTPBadRequest(
                    'Name exists',
                    'Could not create firewall address due to name already existing'
            )

        resp.status = falcon.HTTP_201
        resp.media = {
            'id': model.id
        }


class FirewallDeviceResource(BaseResource):

    def on_get(self, req, resp):
        from sdnms_api.backends.manager import BackendManager
        m = BackendManager()
        m.use_firewall()
        res = m.call_firewall(method='info')
        resp.media = res
