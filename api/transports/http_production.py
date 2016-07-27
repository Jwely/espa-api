from flask import request, make_response, jsonify
from flask.ext.restful import Api, Resource, reqparse, fields, marshal

from api.interfaces.production.version0 import API
from api.domain import api_operations_v0

espa = API()


def whitelist(func):
    """
    Provide a decorator to enact a white filter on an endpoint

    References http://flask.pocoo.org/docs/0.11/deploying/wsgi-standalone/#proxy_setups
    and http://github.com/mattupsate/flask-security
    """
    def decorated(*args, **kwargs):
        white_ls = espa.get_production_whitelist()
        if 'X-Forwarded-For' in request.headers:
            remote_addr = request.headers.getlist('X-Forwarded-For')[0].rpartition(' ')[-1]
        else:
            remote_addr = request.remote_addr or 'untrackable'

        if remote_addr in white_ls:
            return func(*args, **kwargs)
        else:
            return make_response(jsonify({'msg': 'Access Denied'}), 403)
    return decorated


class ProductionVersion(Resource):
    decorators = [whitelist]
    def get(self):
        if 'v0' in request.url:
            return api_operations_v0['production']
        else:
            return espa.api_versions()


class ProductionOperations(Resource):
    decorators = [whitelist]
    def get(self):
        if 'products' in request.url:
            # request.args is an ImmutableMultiDict
            params = request.args.to_dict(flat=True)
            return espa.fetch_production_products(params)
        elif 'handle-orders' in request.url:
            return espa.handle_orders()


    # Probably best to split these up into their own classes
    def post(self, action=None):
        # in testing, request.form always empty. post call looks like:
        # app.post(url, data=json.dumps(data_dict), headers=self.headers)
        #params = request.form.to_dict(flat=True)
        params = request.get_json(force=True)
        if 'queue-products' in request.url:
            return espa.queue_products(**params)
        elif action:
            return espa.update_product_details(action, params)


class ProductionConfiguration(Resource):
    decorators = [whitelist]
    def get(self, key):
        return espa.get_production_key(key)
