#!/usr/bin/env python

import unittest
from api.ordering.version0 import API
from api.utils import get_cfg
from api.dbconnect import DBConnect

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

    def tearDown(self):
        # close the connection
        db = None

    def test_api_versions_type(self):
        self.assertIsInstance(api.api_versions(), dict)

    def test_api_versions_key_val(self):
        self.assertEqual(api.api_versions().keys()[0], 'versions')

    def test_get_available_products_key_val(self):
        self.assertEqual(api.available_products(self.product_id).keys()[0], "tm")

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
    good = {"inputs": ["LE70290302003123EDC00", "LT50290302002123EDC00", 'LO80290302002123EDC00'],
            "products": ["tm_sr", "etm_sr", 'oli_toa'],
            "projection": {"name": "aea",
                           "standard_parallel_1": 29.5,
                           "standard_parallel_2": 45.5,
                           "central_meridian": -96.0,
                           "latitude_of_origin": 23.0,
                           "false_easting": 0.0,
                           "false_northing": 0.0},
            "image_extents": {"maxy": 3164800.0,
                              "miny": 3014800.0,
                              "maxx": -2415600.0,
                              "minx": -2565600.0,
                              'units': 'meters'},
            "format": "gtiff",
            "resize": {"pixel_size": 60.0,
                       "pixel_size_units": "meters"},
            "resampling_method": "nn"}

    def test_validation_get_order_schema(self):
        self.assertIsInstance(api.validation.schema, dict)

    def test_validation_get_valid_options(self):
        self.assertIsInstance(api.validation.valid_params, dict)

    def test_validate_good_order(self):
        self.assertTrue(api.validation(self.good))

    def test_validate_bad_order(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
