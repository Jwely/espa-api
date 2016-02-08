#!/usr/bin/env python
import unittest
import yaml

from api.ordering.version0 import API
from api.utils import api_cfg
from api.dbconnect import DBConnect
import version0_testorders as testorders
from api.providers.validation import validation_schema
from api.providers.validation import ValidationException
import psycopg2.extras

api = API()

class TestAPI(unittest.TestCase):
    def setUp(self):
        db = DBConnect(**api_cfg())
        uidsql = "select user_id, orderid from ordering_order limit 1;"
        unmsql = "select username, email from auth_user where id = %s;"
        db.select(uidsql)
        self.userid = db[0]['user_id']
        self.orderid = db[0]['orderid']
        db.select(unmsql % self.userid)
        self.username = db[0]['username']
        self.usermail = db[0]['email']
        self.product_id = 'LT50150401987120XXX02'
        self.staff_product_id = 'LE70450302003206EDC01'
        staffusersql = "select username, email, is_staff from auth_user where is_staff = True limit 1;"
        pubusersql = "select username, email, is_staff from auth_user where is_staff = False limit 1;"
        db.select(staffusersql)
        self.staffuser = db[0]['username']
        db.select(pubusersql)
        self.pubuser = db[0]['username']
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
        none_user = "this_is_from_testing"
        self.assertIn("msg", api.available_products(self.product_id, none_user).keys())

    def test_fetch_user_orders_by_email_val(self):
        orders = api.fetch_user_orders(self.usermail)
        self.assertEqual(orders.keys()[0], "orders")

    def test_fetch_user_orders_by_username_val(self):
        orders = api.fetch_user_orders(self.username)
        self.assertEqual(orders.keys()[0], "orders")

    def test_fetch_order_by_orderid_val(self):
        order = api.fetch_order(self.orderid)
        self.assertEqual(order['orderid'], self.orderid)

    def test_fetch_order_status_valid(self):
        response = api.order_status(self.orderid)
        self.assertEqual(response.keys(), ['orderid', 'status'])

    def test_fetch_order_status_invalid(self):
        invalid_orderid = 'invalidorderid'
        response = api.order_status(invalid_orderid)
        self.assertEqual(response.keys(), ['msg'])

class TestValidation(unittest.TestCase):
    def setUp(self):
        db = DBConnect(**api_cfg())
        uidsql = "select user_id, orderid from ordering_order limit 1;"
        unmsql = "select username, email from auth_user where id = %s;"
        db.select(uidsql)
        self.userid = db[0]['user_id']
        self.orderid = db[0]['orderid']
        db.select(unmsql % self.userid)
        self.username = db[0]['username']
        self.usermail = db[0]['email']
        self.product_id = 'LT50150401987120XXX02'
        self.staff_product_id = 'LE70450302003206EDC01'
        staffusersql = "select username, email, is_staff from auth_user where is_staff = True limit 1;"
        pubusersql = "select username, email, is_staff from auth_user where is_staff = False limit 1;"
        db.select(staffusersql)
        self.staffuser = db[0]['username']
        db.select(pubusersql)
        self.pubuser = db[0]['username']
        with open('api/domain/restricted.yaml') as f:
            self.restricted_list = yaml.load(f.read())

        self.base_order = testorders.build_base_order()
        self.base_schema = validation_schema.Version0Schema().request_schema

    def test_validation_get_order_schema(self):
        self.assertIsInstance(api.validation.fetch_order_schema(), dict)

    def test_validation_get_valid_formats(self):
        self.assertIsInstance(api.validation.fetch_formats(), dict)

    def test_validation_get_valid_resampling(self):
        self.assertIsInstance(api.validation.fetch_resampling(), dict)

    def test_validation_get_valid_projections(self):
        self.assertIsInstance(api.validation.fetch_projections(), dict)

    def test_validate_good_order(self):
        self.assertIsNone(api.validation(self.base_order, self.staffuser))

    def test_validate_bad_orders(self):
        # for bad in testorders.test_assertion_failures(self.base_order, self.base_schema):
        #     with self.assertRaises(ValidationException):
        #         api.validation(bad, self.staffuser)

        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
