from flask_apscheduler import APScheduler
from api.providers.caching.caching_provider import CachingProvider
from api.interfaces.production.version1 import API
import yaml

api = API()


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
    products = api.fetch_production_products({'product_types': ['landsat', 'modis'],
                                              'record_limit': 50})
    return True


def plots_to_process():
    products = api.fetch_production_products({'product_types': ['plot'],
                                              'record_limit': 50})
    return True


def handle_orders():
    response = api.handle_orders()
    return True
