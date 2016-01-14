#!/usr/bin/env python

import unittest
from api.ordering.version0 import API

api = API()


class TestAPI(unittest.TestCase):
    def setUp(self):
        pass

    def test_api_info_type(self):
        # self.assertIsInstance(api.api_info(), dict)
        pass

    def test_api_info_key_val(self):
        # self.assertEqual(api.api_info().keys(), ['version_0'])
        pass

    def test_get_available_products_type(self):
        product_id = 'LT50150401987120XXX02'
        self.assertIsInstance(api.available_products(product_id), dict)

    def test_get_available_products_key_val(self):
        product_id = 'LT50150401987120XXX02'
        self.assertEqual(api.available_products(product_id).keys()[0], "tm")


class TestValidation(unittest.TestCase):
    good = {"inputs": ["LE70290302003123EDC00", "LT50290302002123EDC00"],
            "products": ["tm_sr", "etm_sr"],
            "projection": {"name": "aea",
                           "standard_parallel_1": 29.5,
                           "standard_parallel_2": 45.5,
                           "central_meridian": -96.0,
                           "latitude_of_origin": 23.0,
                           "false_easting": 0.0,
                           "false_northing": 0.0},
            "image_extents": {
                "maxy": 3164800.0,
                "miny": 3014800.0,
                "maxx": -2415600.0,
                "minx": -2565600.0},
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
