from flask_apscheduler import APScheduler
from api.providers.caching.caching_provider import CachingProvider
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.interfaces.production.version1 import API
from api.system.logger import ilogger as logger
from api.transports.broker_production import ProductionPublisher, ProductionConsumer
import yaml

api = API()
cache = CachingProvider()
config = ConfigurationProvider()
production_publisher = ProductionPublisher()

expiry_default = 1800 # 30 minutes


class Scheduling(APScheduler):

    def __init__(self):
        super(Scheduling, self).__init__()

        with open('api/domain/jobs.yaml') as f:
            _jobs = yaml.load(f.read())['jobs']

        for _j in _jobs:
            self.add_job(**{
                'id': _j,
                'func': 'api.system.scheduling:'+_j,
                'trigger': 'interval',
                _jobs[_j]['units']: _jobs[_j]['interval']
            })


def products_to_process():
    if config.get('system.ondemand_enabled') != 'True':
        logger.warn(''' system.ondemand_enabled is not 'True',
                    skipping scheduling.products_to_process ''')
        return

    cache_key = 'prod_to_proc'
    if cache.get(cache_key):
        logger.warn(''' last scheduling call to products_to_process
                    does not appear complete, skipping...''')
    else:
        logger.info("setting cache_key: {}".format(cache_key))
        cache.set(cache_key, 1, 1800)
        products = api.fetch_production_products({'product_types': ['landsat', 'modis'],
                                                  'record_limit': 50})
        logger.info("found {} products to process...".format(len(products)))
        production_publisher.publish('products_to_process', products)
        logger.info("deleting cache_key: {}".format(cache_key))
        if cache.delete(cache_key):
            logger.info("successfully delete key..")
    return True


def plots_to_process():
    if config.get('system.ondemand_enabled') != 'True':
        logger.warn(''' system.ondemand_enabled is not 'True',
                    skipping scheduling.plots_to_process ''')
        return

    # set cache key to avoid process collision
    products = api.fetch_production_products({'product_types': ['plot'],
                                              'record_limit': 50})
    return True


def handle_orders():
    if config.get('system.order_disposition_enabled') != 'True':
        logger.warn(''' system.order_disposition_enabled is not 'True',
                    skipping scheduling.handle_orders ''')
        return

    # set cache key to avoid process collision
    response = api.handle_orders()
    return True
