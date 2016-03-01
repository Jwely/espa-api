#!/usr/bin/env python
import unittest
import yaml
import copy
import re
import os

from api.ordering.version0 import API
from api.domain.utils import api_cfg, lowercase_all
from api.domain.dbconnect import DBConnect
import version0_testorders as testorders
from api.providers.validation import validation_schema
from api.api_except import ValidationException
import psycopg2.extras

from api.domain.mock_order import MockOrder

api = API()

class TestProductionAPI(unittest.TestCase):
    def setUp(self):
        os.environ['espa_api_testing'] = 'True'
        MockOrder.generate_testing_orders()

    def tearDown(self):
        os.environ['espa_api_testing'] = ''
        MockOrder.tear_down_testing_orders()

    def test_fetch_production_products_modis(self):
        pass

    def test_fetch_production_products_landsat(self):
        pass

    def test_fetch_production_products_plot(self):
        pass

    def test_update_product_details_update_status(self):
        pass

    def test_update_product_details_set_product_error(self):
        pass

    def test_update_product_details_set_product_unavailable(self):
        pass

    def test_update_product_details_mark_product_complete(self):
        pass

    def test_handle_orders_success(self):
        pass

    def test_handle_orders_fail(self):
        pass

    def queue_products_success(self):
        pass

    def queue_products_fail(self):
        pass

    def get_production_key(self):
        pass










if __name__ == '__main__':
    unittest.main(verbosity=2)
