#!/usr/bin/env python
import os
import unittest

from api.domain.mocks.order import MockOrder
from api.domain.mocks.user import MockUser
from api.interfaces.ordering.version0 import API

api = API()

class TestProductionAPI(unittest.TestCase):
    def setUp(self):
        os.environ['espa_api_testing'] = 'True'
        # create a user
        self.mock_user = MockUser()
        self.mock_order = MockOrder()
        self.user_id = mock_user.add_testing_user()


    def tearDown(self):
        # clean up orders
        self.mock_order.tear_down_testing_orders()
        # clean up users
        self.mock_user.cleanup()
        os.environ['espa_api_testing'] = ''

    def test_fetch_production_products_modis(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)


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
