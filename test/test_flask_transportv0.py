#!/usr/bin/env python

import os
import json
import unittest
import tempfile

from api import transport

class TransportTestCase(unittest.TestCase):

    def setUp(self):
        self.app = transport.app.test_client()
        self.sceneids = ('LT50150401987120XXX02','LE70450302003206EDC01')

    def tearDown(self):
        pass

    def test_get_api_response_type(self):
        response = self.app.get('/api')
        assert response.content_type == 'application/json'

    def test_get_api_response_content(self):
        response = self.app.get('/api')
        assert 'versions' in json.loads(response.get_data()).keys()

    def test_get_api_info_response_type(self):
        response = self.app.get('/api/v0')
        assert response.content_type == 'application/json'

    def test_get_api_info_response_content(self):
        response = self.app.get('/api/v0')
        resp_json = json.loads(response.get_data())
        assert "Version 0" in resp_json['description']

    def test_get_available_prods(self):
        url = '/api/v0/available-products/' + ",".join(self.sceneids)
        response = self.app.get(url)
        assert response.content_type == 'application/json'

if __name__ == '__main__':
    unittest.main()
