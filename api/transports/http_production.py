from flask import request
from flask.ext.restful import Api, Resource, reqparse, fields, marshal

from api.interfaces.production.version0 import API
from api.domain import api_operations_v0

espa = API()

class ProductionVersion(Resource):
    def get(self):
        if 'v0' in request.url:
            return api_operations_v0['production']
        else:
            return espa.api_versions()


class ProductionOperations(Resource):
    def get(self):
        if 'products' in request.url:
            # request.args is an ImmutableMultiDict
            params = request.args.to_dict(flat=True)
            return espa.fetch_production_products(params)

    # Probably best to split these up into their own classes
    def post(self, action=None):
        # in testing, request.form always empty. post call looks like:
        # app.post(url, data=json.dumps(data_dict), headers=self.headers)
        #params = request.form.to_dict(flat=True)
        params = request.get_json(force=True)
        if 'handle-orders' in request.url:
            return espa.handle_orders()
        elif 'queue-products' in request.url:
            return espa.queue_products(**params)
        elif action:
            return espa.update_product_details(action, params)


class ProductionConfiguration(Resource):
    def get(self, key):
        return espa.get_production_key(key)
