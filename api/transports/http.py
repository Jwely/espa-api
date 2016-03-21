# Tie together the urls for functionality

import os

from flask import Flask
from flask.ext.restful import Api, Resource, reqparse, fields, marshal

from api.system.config import ApiConfig
from http_user import Index, VersionInfo,\
    AvailableProducts, ValidationInfo, ListOrders, Ordering, UserInfo, ItemStatus
from http_production import ProductionVersion, ProductionConfiguration, ProductionOperations
#from http_production import ...

config = ApiConfig()

app = Flask(__name__)
app.secret_key = config.cfg['key']

if config.mode == 'dev' or os.environ.get('ESPA_DEBUG'):
    app.debug = True

errors = {'NotFound': {'message': 'The requested URL was not found on the server.',
                       'status': 404}}


transport_api = Api(app, errors=errors, catch_all_404s=True)

# USER facing functionality

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
                           '/api/v0/order/',
                           '/api/v0/order/<ordernum>',
                           '/api/v0/order-status/<ordernum>')

transport_api.add_resource(UserInfo,
                           '/api/v0/user',
                           '/api/v0/user/')

transport_api.add_resource(ItemStatus,
                           '/api/v0/item-status/<orderid>',
                           '/api/v0/item-status/<orderid>/<itemnum>')


# PRODUCTION facing functionality
transport_api.add_resource(ProductionVersion,
                           '/production-api',
                           '/production-api/v0')

transport_api.add_resource(ProductionOperations,
                           '/production-api/v0/products',
                           '/production-api/v0/<action>',
                           '/production-api/v0/handle-orders',
                           '/production-api/v0/queue-products')

transport_api.add_resource(ProductionConfiguration,
                           '/production-api/v0/configuration/<key>')


if __name__ == '__main__':
    app.run()
