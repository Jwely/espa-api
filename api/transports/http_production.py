import flask
from flask import Flask, jsonify, abort, make_response, request
from flask.ext.restful import Api, Resource, reqparse, fields, marshal

from api.interfaces.ordering.version0 import API
from api.domain.user import User
from api.system.config import ApiConfig
from api.util import lowercase_all
from api.domain import api_operations_v0


espa = API()

# Contain Production/Internal facing REST functionality
# '/production-api', methods=['GET']
# '/production-api/v0', methods=['GET']
# '/production-api/v0/products', methods=['GET']
# '/production-api/v0/<action>', methods=['POST']
# '/production-api/v0/handle-orders', methods=['POST']
# '/production-api/v0/queue-products', methods=['POST']
# '/production-api/v0/configuration/<key>', methods=['GET']

class ProductionVersion(Resource):
    def get(self):
        if 'v0' in request.url:
            return api_operations_v0['production']
        else:
            return espa.api_versions()


class ProductionOperations(Resource):
    def get(self):
        if 'products' in request.url:
            return espa.fetch_production_products(request.args)


    def post(self, action=None):
        if 'handle-orders' in request.url:
            return espa.handle_orders()
        elif 'queue-products' in request.url:
            return espa.queue_products(request.form)
        elif action:
            return espa.update_product_details(action, request.form)


class ProductionConfiguration(Resource):
    def get(self, key):
        return espa.get_production_key(key)