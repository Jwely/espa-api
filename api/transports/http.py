# Tie together the urls for functionality

import os

from flask import Flask, request
from flask.ext.restful import Api, Resource, reqparse, fields, marshal

from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.util import api_cfg
from api.system.scheduling import Scheduling

from http_user import Index, VersionInfo, AvailableProducts, ValidationInfo,\
    ListOrders, Ordering, UserInfo, ItemStatus

from http_production import ProductionVersion, ProductionConfiguration, ProductionOperations, ProductionManagement

from http_admin import Reports, SystemStatus, OrderResets

from broker_production import ProductionConsumer

config = ConfigurationProvider()

app = Flask(__name__)
app.secret_key = api_cfg('config').get('key')

##################################
## Scheduled asynchronous tasks ##
##################################
scheduler = Scheduling()
scheduler.init_app(app)
scheduler.start()

###############################################
## RabbitMQ Consumer for Production Messages ##
###############################################
production_consumer = ProductionConsumer()
production_consumer.consume()

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
                           '/api/v<version>/available-products/<prod_id>',
                           '/api/v<version>/available-products')

transport_api.add_resource(ValidationInfo,
                           '/api/v<version>/projections',
                           '/api/v<version>/formats',
                           '/api/v<version>/resampling-methods',
                           '/api/v<version>/order-schema')

transport_api.add_resource(ListOrders,
                           '/api/v<version>/list-orders',
                           '/api/v<version>/list-orders/',
                           '/api/v<version>/list-orders/<email>',
                           '/api/v<version>/list-orders-ext',
                           '/api/v<version>/list-orders-ext/',
                           '/api/v<version>/list-orders-ext/<email>',
                           '/api/v<version>/list-orders-feed/<email>')

transport_api.add_resource(Ordering,
                           '/api/v<version>/order',
                           '/api/v<version>/order/',
                           '/api/v<version>/order/<ordernum>',
                           '/api/v<version>/order-status/<ordernum>')

transport_api.add_resource(UserInfo,
                           '/api/v<version>/user',
                           '/api/v<version>/user/')

transport_api.add_resource(ItemStatus,
                           '/api/v<version>/item-status/<orderid>',
                           '/api/v<version>/item-status/<orderid>/<itemnum>')

transport_api.add_resource(Reports,
                           '/api/v<version>/reports/',
                           '/api/v<version>/reports/<name>/',
                           '/api/v<version>/statistics/',
                           '/api/v<version>/statistics/<name>',
                           '/api/v<version>/aux_report/<group>/',
                           '/api/v<version>/aux_report/<group>/<year>')

transport_api.add_resource(SystemStatus,
                           '/api/v<version>/system-status',
                           '/api/v<version>/system-status-update',
                           '/api/v<version>/system/config')

transport_api.add_resource(OrderResets,
                           '/api/v<version>/error_to_submitted/<orderid>',
                           '/api/v<version>/error_to_unavailable/<orderid>')

# PRODUCTION facing functionality
transport_api.add_resource(ProductionVersion,
                           '/production-api',
                           '/production-api/v<version>')

transport_api.add_resource(ProductionOperations,
                           '/production-api/v<version>/products',
                           '/production-api/v<version>/<action>',
                           '/production-api/v<version>/handle-orders',
                           '/production-api/v<version>/queue-products')

transport_api.add_resource(ProductionManagement,
                           '/production-api/v<version>/handle-orphans')

transport_api.add_resource(ProductionConfiguration,
                           '/production-api/v<version>/configuration/<key>')


if __name__ == '__main__':

    debug = False
    if 'ESPA_DEBUG' in os.environ and os.environ['ESPA_DEBUG'] == 'True':
        debug = True
        app.run(debug=debug)

