from flask import request, make_response, jsonify
from flask.ext.restful import Api, Resource, reqparse, fields, marshal

from api.interfaces.production.version0 import API
from api.domain import api_operations_v0, default_error_message

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


def prep_response(response):
    """
    return the correct response code, based on response content
    :param response:
    :return: response, response code
    """
    resp_code = 500 if response == default_error_message else 200
    return response, resp_code


class ProductionVersion(Resource):
    decorators = [whitelist]

    @staticmethod
    def get():
        if 'v0' in request.url:
            resp = api_operations_v0['production']
        else:
            resp = espa.api_versions()

        return prep_response(resp)


class ProductionOperations(Resource):
    decorators = [whitelist]

    @staticmethod
    def get():
        if 'products' in request.url:
            params = request.args.to_dict(flat=True)
            resp = espa.fetch_production_products(params)
        elif 'handle-orders' in request.url:
            resp = espa.handle_orders()

        return prep_response(resp)

    @staticmethod
    def post(action=None):
        params = request.get_json(force=True)
        if 'queue-products' in request.url:
            resp = espa.queue_products(**params)
        elif action:
            resp = espa.update_product_details(action, params)

        return prep_response(resp)


class ProductionConfiguration(Resource):
    decorators = [whitelist]

    @staticmethod
    def get(key):
        resp = espa.get_production_key(key)
        return prep_response(resp)


class ProductionManagement(Resource):
    decorators = [whitelist]

    @staticmethod
    def get():
        if 'handle-orphans' in request.url:
            resp = espa.catch_orphaned_scenes()
            return prep_response(resp)
