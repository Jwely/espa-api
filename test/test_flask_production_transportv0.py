#!/usr/bin/env python

import os
import json
import unittest
import tempfile

from api.util import api_cfg
from api.util.dbconnect import DBConnect
from api.transports import http

class ProductionTransportTestCase(unittest.TestCase):

    def setUp(self):
        cfg = api_cfg()
        self.app = http.app.test_client()
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

    def test_get_production_api(self):
        pass

    def test_get_production_api_v0(self):
        pass

    def test_get_production_api_products_modis(self):
        pass

    def test_get_production_api_products_landsat(self):
        pass

    def test_get_production_api_products_plot(self):
        pass

    def test_post_production_api_update_status(self):
        pass

    def test_post_production_api_set_product_error(self):
        pass

    def test_post_production_api_set_product_unavailable(self):
        pass

    def test_post_production_api_mark_product_complete(self):
        pass

    def test_post_production_api_handle_orders(self):
        pass

    def test_post_production_api_queue_products(self):
        pass

    def test_get_production_api_configurations(self):
        pass




