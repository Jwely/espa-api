#!/usr/bin/env python
import os
import unittest

from mock import patch
from api.external.mocks import lta, lpdaac

from api.domain.mocks.order import MockOrder
from api.domain.mocks.user import MockUser
from api.domain.user import User
from api.interfaces.ordering.version0 import API
from api.providers.ordering.mocks.production_provider import MockProductionProvider

from api.providers.ordering.production_provider import ProductionProvider

api = API()
production_provider = ProductionProvider()
mock_production_provider = MockProductionProvider()

class TestProductionAPI(unittest.TestCase):
    def setUp(self):
        os.environ['espa_api_testing'] = 'True'
        # create a user
        self.mock_user = MockUser()
        self.mock_order = MockOrder()
        self.user_id = self.mock_user.add_testing_user()


    def tearDown(self):
        # clean up orders
        self.mock_order.tear_down_testing_orders()
        # clean up users
        self.mock_user.cleanup()
        os.environ['espa_api_testing'] = ''

    def test_fetch_production_products_modis(self):
        pass

    @patch('api.external.lta.get_download_urls', lta.get_download_urls)
    @patch('api.external.lpdaac', lpdaac)
    @patch('api.providers.ordering.production_provider.ProductionProvider.set_product_retry', mock_production_provider.set_product_retry)
    def test_fetch_production_products_landsat(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        # need scenes with statuses of 'processing' and 'ordered'
        self.mock_order.update_scenes(order_id, 'status', ['processing','ordered','oncache'])
        user = User.where("id = {0}".format(self.user_id))[0]
        params = {'for_user': user.username, 'product_types': ['landsat']}

        # api.fetch_production_products calls to ->
        response = production_provider.get_products_to_process(**params)
        self.assertTrue('bilbo' in response[0]['orderid'])


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
