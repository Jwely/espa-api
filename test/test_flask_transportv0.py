#!/usr/bin/env python

import os
import json
import unittest
import tempfile
import transport

from api.utils import api_cfg
from api.dbconnect import DBConnect


class TransportTestCase(unittest.TestCase):

    def setUp(self):
        cfg = api_cfg()
        self.app = transport.app.test_client()
        self.app.testing = True
        self.sceneids = ('LT50150401987120XXX02','LE70450302003206EDC01')
        auth_string = "%s:%s" % (cfg['devuser'],cfg['devword'])
        self.headers = {"Authorization": auth_string}
        self.useremail = cfg['devmail']
        db = DBConnect(**cfg)
        uidsql = "select user_id, orderid from ordering_order limit 1;"
        unmsql = "select username, email from auth_user where id = %s;"
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

    def tearDown(self):
        pass

    def test_get_api_response_type(self):
        response = self.app.get('/api', headers=self.headers)
        assert response.content_type == 'application/json'

    def test_get_api_response_content(self):
        response = self.app.get('/api', headers=self.headers)
        assert 'versions' in json.loads(response.get_data()).keys()

    def test_get_api_info_response_type(self):
        response = self.app.get('/api/v0', headers=self.headers)
        assert response.content_type == 'application/json'

    def test_get_api_info_response_content(self):
        response = self.app.get('/api/v0', headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert "Version 0" in resp_json['description']

    def test_get_available_prods(self):
        url = '/api/v0/available-products/' + ",".join(self.sceneids)
        response = self.app.get(url, headers=self.headers)
        assert response.content_type == 'application/json'

    def test_post_available_prods(self):
        url = '/api/v0/available-products'
        data_dict = {'product_ids': ",".join(self.sceneids)}
        response = self.app.post(url, data=data_dict, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert "tm5" in resp_json.keys()

    def test_get_available_orders_user(self):
        url = "/api/v0/orders"
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert resp_json.keys() == ['orders']

    def test_get_available_orders_email(self):
        # email param comes in as unicode
        url = "/api/v0/orders/" + str(self.useremail)
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert resp_json.keys() == ['orders']

    def test_get_order_by_ordernum(self):
        url = "/api/v0/order/" + str(self.orderid)
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'orderid' in resp_json.keys()

    def test_get_order_status_by_ordernum(self):
        url = "/api/v0/order-status/" + str(self.orderid)
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'orderid' in resp_json.keys()

    def test_get_item_status_by_ordernum(self):
        url = "/api/v0/item-status/%s" % self.itemorderid
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'orderid' in resp_json.keys()

    def test_get_item_status_by_ordernum_itemnum(self):
        url = "/api/v0/item-status/%s/%s" % (self.itemorderid, self.itemid)
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'orderid' in resp_json.keys()

    def test_get_current_user(self):
        url = "/api/v0/user"
        response = self.app.get(url, headers=self.headers)
        resp_json = json.loads(response.get_data())
        assert 'username' in resp_json.keys()

if __name__ == '__main__':
    unittest.main()


