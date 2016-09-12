import unittest
from mock import patch

from api.providers.metrics.metrics_provider import MetricsProvider


class TestMetrics(unittest.TestCase):
    def setUp(self):
        self.begin = '1985-1-1'
        self.end = '1985-1-31'

        self.downloadboiler_info = {'tot_dl': 1,
                                    'tot_vol': 1}

        self.ondemandboiler_info = {'who': 'espa',
                                    'scenes_month': 1,
                                    'scenes_non': 1,
                                    'order_month': 1,
                                    'orders_usgs': 1,
                                    'orders_non': 1,
                                    'tot_unique': 1}

        self.prodboiler_info = {'title': 'yes',
                                'total': 1,
                                'sr': 1,
                                'bt': 1,
                                'toa': 1,
                                'l1': 1,
                                'source_metadata': 1,
                                'customized_source_data': 1,
                                'sr_evi': 1,
                                'sr_msavi': 1,
                                'sr_nbr': 1,
                                'sr_nbr2': 1,
                                'sr_ndmi': 1,
                                'sr_ndvi': 1,
                                'sr_savi': 1,
                                'cloud': 1,
                                'plot': 1}


