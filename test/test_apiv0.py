#!/usr/bin/env python

import unittest
from api.ordering.version0 import API

api = API()

class TestAPI(unittest.TestCase):

    def setUp(self):
       pass

    def test_api_versions_type(self):
        self.assertIsInstance( api.api_versions(), dict ) 

    def test_api_versions_key_val(self):
        self.assertEqual( api.api_versions().keys()[0], 'versions' ) 

    def test_get_available_products_type(self):
        product_id = 'LT50150401987120XXX02'
        self.assertIsInstance( api.available_products(product_id), dict )

    def test_get_available_products_key_val(self):
        product_id = 'LT50150401987120XXX02'
        self.assertEqual( api.available_products(product_id).keys()[0], "tm" )

    def test_fetch_user_orders_type(self):
	self.assertIsInstance(api.fetch_user_orders('jane.doe@usgs.gov'), dict)

    def test_fetch_order_type(self):
	self.assertIsInstance(api.fetch_order('abc123'), dict)

if __name__ == '__main__':
    unittest.main()


