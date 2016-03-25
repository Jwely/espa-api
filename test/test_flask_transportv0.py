#!/usr/bin/env python

import os
import json
import unittest
import base64

import version0_testorders as testorders

from mock import patch

from api.transports import http
from api.util import lowercase_all
from api.util.dbconnect import db_instance
from api.domain.user import User
from api.domain.mocks.order import MockOrder
from api.domain.mocks.user import MockUser

from api.interfaces.ordering.mocks.version0 import MockAPI
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.providers.ordering.mocks.ordering_provider import MockOrderingProvider

mock_api = MockAPI()
mock_ordering_provider = MockOrderingProvider()

class TransportTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['espa_api_testing'] = 'True'
        # create a user
        self.mock_user = MockUser()
        self.mock_order = MockOrder()
        self.user_id = self.mock_user.add_testing_user()
        self.order_id = self.mock_order.generate_testing_order(self.user_id)

        cfg = ConfigurationProvider()
        self.app = http.app.test_client()
        self.app.testing = True

        self.sceneids = self.mock_order.scene_names_list(self.order_id)[0:2]

        self.user = User.where("id = {0}".format(self.user_id))[0]

        token = ''.format(self.user.username, 'foo')
        auth_string = "Basic {}".format(base64.b64encode(token))
        self.headers = {"Authorization": auth_string}

        self.user.email

        with db_instance() as db:
            uidsql = "select user_id, orderid from ordering_order limit 1;"
            db.select(uidsql)
            self.userid = db[0]['user_id']
            self.orderid = db[0]['orderid']

            itemsql = "select name, order_id from ordering_scene limit 1;"
            db.select(itemsql)
            self.itemid = db[0][0]
            itemorderid = db[0][1]

            ordersql = "select orderid from ordering_order where id = {};".format(itemorderid)
            db.select(ordersql)
            self.itemorderid = db[0][0]

        self.base_order = lowercase_all(testorders.build_base_order())

    def tearDown(self):
        # clean up orders
        self.mock_order.tear_down_testing_orders()
        # clean up users
        self.mock_user.cleanup()
        os.environ['espa_api_testing'] = ''

    def test_get_api_response_type(self):
        response = self.app.get('/api', headers=self.headers)
        assert response.content_type == 'application/json'

    def test_get_api_response_content(self):
        response = self.app.get('/api', headers=self.headers)
        assert 'versions' in json.loads(response.get_data()).keys()

    @patch('api.domain.user.User.get', MockUser.get)
    def test_get_api_info_response_content(self):
        response = self.app.get('/api/v0', headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert "Version 0" in resp_json['description']

    @patch('api.domain.user.User.get', MockUser.get)
    @patch('api.providers.ordering.ordering_provider.OrderingProvider.available_products', mock_api.available_products)
    def test_get_available_prods(self):
        url = '/api/v0/available-products/' + ",".join(self.sceneids)
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert "etm" in resp_json.keys()

    @patch('api.domain.user.User.get', MockUser.get)
    @patch('api.providers.ordering.ordering_provider.OrderingProvider.available_products', mock_api.available_products)
    def test_post_available_prods(self):
        url = '/api/v0/available-products'
        data_dict = {'inputs': self.sceneids}
        response = self.app.post(url, data=json.dumps(data_dict), headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert "etm" in resp_json.keys()

    @patch('api.domain.user.User.get', MockUser.get)
    @patch('api.providers.ordering.ordering_provider.OrderingProvider.fetch_user_orders', mock_ordering_provider.fetch_user_orders)
    def test_get_available_orders_user(self):
        url = "/api/v0/list-orders"
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert resp_json.keys() == ['orders']

    @patch('api.domain.user.User.get', MockUser.get)
    def test_get_available_orders_email(self):
        # email param comes in as unicode
        url = "/api/v0/list-orders/" + str(self.user.email)
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert resp_json.keys() == ['orders']

    @patch('api.domain.user.User.get', MockUser.get)
    def test_get_order_by_ordernum(self):
        url = "/api/v0/order/" + str(self.orderid)
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'orderid' in resp_json.keys()

    @patch('api.domain.user.User.get', MockUser.get)
    def test_get_order_status_by_ordernum(self):
        url = "/api/v0/order-status/" + str(self.orderid)
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'orderid' in resp_json.keys()

    @patch('api.domain.user.User.get', MockUser.get)
    def test_get_item_status_by_ordernum(self):
        url = "/api/v0/item-status/%s" % self.itemorderid
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'orderid' in resp_json.keys()

    @patch('api.domain.user.User.get', MockUser.get)
    def test_get_item_status_by_ordernum_itemnum(self):
        url = "/api/v0/item-status/%s/%s" % (self.itemorderid, self.itemid)
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'orderid' in resp_json.keys()

    @patch('api.domain.user.User.get', MockUser.get)
    def test_get_current_user(self):
        url = "/api/v0/user"
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'username' in resp_json.keys()

    @patch('api.domain.user.User.get', MockUser.get)
    def test_get_projections(self):
        url = '/api/v0/projections'
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'aea' in resp_json.keys()

    @patch('api.domain.user.User.get', MockUser.get)
    def test_get_formats(self):
        url = '/api/v0/formats'
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'formats' in resp_json.keys()

    @patch('api.domain.user.User.get', MockUser.get)
    def test_get_resampling(self):
        url = '/api/v0/resampling-methods'
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'resampling_methods' in resp_json.keys()

    @patch('api.domain.user.User.get', MockUser.get)
    def test_get_order_schema(self):
        url = '/api/v0/order-schema'
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'properties' in resp_json.keys()

    # Waiting for DB mock-ups to be finished
    def test_post_order(self):
        pass
        # url = '/api/v0/order'
        #
        # header = copy.deepcopy(self.headers)
        #
        #
        # response = self.app.get(url)

if __name__ == '__main__':
    unittest.main()


