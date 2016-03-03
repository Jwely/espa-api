import os

from flask import Flask, jsonify, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal

from api.domain.config import ApiConfig
from http_restful import Index, VersionInfo,\
    AvailableProducts, ValidationInfo, ListOrders, Ordering

config = ApiConfig()

app = Flask(__name__)
app.secret_key = config.cfg['key']

if config.mode == 'dev' or os.environ.get('ESPA_DEBUG'):
    app.debug = True

errors = {'NotFound': {'message': 'The requested URL was not found on the server.',
                       'status': 404}}


transport_api = Api(app, errors=errors, catch_all_404s=True)

transport_api.add_resource(Index, '/')

transport_api.add_resource(VersionInfo,
                           '/api',
                           '/api/',
                           '/api/v<version>')

transport_api.add_resource(AvailableProducts,
                           '/api/v0/available-products/<prod_id>',
                           '/api/v0/available-products')

transport_api.add_resource(ValidationInfo,
                           '/api/v0/projections',
                           '/api/v0/formats',
                           '/api/v0/resampling-methods',
                           '/api/v0/order-schema')

transport_api.add_resource(ListOrders,
                           '/api/v0/list-orders',
                           '/api/v0/list-orders/',
                           '/api/v0/list-orders/<email>')

transport_api.add_resource(Ordering,
                           '/api/v0/order',
                           '/api/v0/order/'
                           '/api/v0/order/<ordernum>')


# /api/v0/user


if __name__ == '__main__':
    app.run()
