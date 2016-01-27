#!/usr/bin/env python
import unittest
import yaml
from api.ordering.version0 import API
from api.utils import get_cfg
from api.dbconnect import DBConnect
import version0_testcases as tc

api = API()

class TestAPI(unittest.TestCase):
    def setUp(self):

        cfg = get_cfg()['config']
        db = DBConnect(**cfg)
        uidsql = "select user_id, orderid from ordering_order limit 1;"
        unmsql = "select username, email from auth_user where id = %s;"
        db.select(uidsql)
        self.userid = db[0][0]
        self.orderid = db[0][1]
        db.select(unmsql % db[0][0])
        self.username = db[0][0]
        self.usermail = db[0][1]
        self.product_id = 'LT50150401987120XXX02'
        self.staff_product_id = 'LE70450302003206EDC01'
        staffusersql = "select username, email, is_staff from auth_user where is_staff = True limit 1;"
        pubusersql = "select username, email, is_staff from auth_user where is_staff = False limit 1;"
        db.select(staffusersql)
        self.staffuser = db[0][0]
        db.select(pubusersql)
        self.pubuser = db[0][0]
        with open('api/domain/restricted.yaml') as f:
            self.restricted_list = yaml.load(f.read())

    def tearDown(self):
        # close the connection
        db = None

    def test_api_versions_type(self):
        self.assertIsInstance(api.api_versions(), dict)

    def test_api_versions_key_val(self):
        self.assertEqual(api.api_versions().keys()[0], 'versions')

    def test_get_available_products_key_val(self):
        self.assertEqual(api.available_products(self.product_id, self.username).keys()[0], "tm5")

    def test_get_available_products_by_staff(self):
        # staff should see all available products
        return_dict = api.available_products(self.staff_product_id, self.staffuser)
        for item in self.restricted_list['internal_only']:
            self.assertTrue(item in return_dict['etm7']['outputs'])

    def test_get_available_products_by_public(self):
        # public should not see products listed in api/domain.restricted.yaml
        return_dict = api.available_products(self.staff_product_id, self.pubuser)
        for item in self.restricted_list['internal_only']:
            self.assertFalse(item in return_dict['etm7']['outputs'])

    def test_get_available_products_by_none(self):
        none_user = "foobar"
        self.assertEqual(api.available_products(self.product_id, none_user), {})

    def test_fetch_user_orders_by_email_val(self):
        orders = api.fetch_user_orders(self.usermail)
        self.assertEqual(orders.keys()[0], "orders")

    def test_fetch_user_orders_by_username_val(self):
        orders = api.fetch_user_orders(self.username)
        self.assertEqual(orders.keys()[0], "orders")

    def test_fetch_order_by_orderid_val(self):
        order = api.fetch_order(self.orderid)
        self.assertEqual(order['orderid'], self.orderid)

class TestValidation(unittest.TestCase):
    def setUp(self):

        cfg = get_cfg()['config']
        with DBConnect(**cfg) as db:
        # db = DBConnect(**cfg)
            uidsql = "select user_id, orderid from ordering_order limit 1;"
            unmsql = "select username, email from auth_user where id = %s;"
            db.select(uidsql)
            self.userid = db[0][0]
            self.orderid = db[0][1]
            db.select(unmsql % db[0][0])
            self.username = db[0][0]
            self.usermail = db[0][1]
            staffusersql = "select username, email, is_staff from auth_user where is_staff = True limit 1;"
            pubusersql = "select username, email, is_staff from auth_user where is_staff = False limit 1;"
            db.select(staffusersql)
            self.staffuser = db[0][0]
            db.select(pubusersql)
            self.pubuser = db[0][0]
            with open('api/domain/restricted.yaml') as f:
                self.restricted_list = yaml.load(f.read())

    def test_validation_get_order_schema(self):
        self.assertIsInstance(api.validation.schema, dict)

    def test_validation_get_valid_options(self):
        self.assertIsInstance(api.validation.valid_params, dict)

    def test_validate_good_order(self):
        self.assertTrue(api.validation(tc.build_base_order(), self.staffuser))

    def test_validate_bad_order(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
