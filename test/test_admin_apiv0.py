import unittest
import os

from api.interfaces.admin import version0

espa = version0.API()


class TestAdminConfiguration(unittest.TestCase):
    def setUp(self):
        os.environ['espa_api_testing'] = 'True'
        base = os.path.dirname(os.path.abspath(__file__))
        self.bfile = os.path.join(base, 'test-backup')

        self.test_key = 'test_key'
        self.test_value = 'test_value'

        self.loaded_key = 'loaded.test_key'
        self.loaded_value = 'loaded.test_value'

        self.test_dump = 'test-db-dump'

        with open(self.test_dump, 'w') as f:
            f.write("INSERT INTO ordering_configuration (key, value) "
                    "VALUES ('{0}', '{1}') "
                    "ON CONFLICT (key) "
                    "DO UPDATE SET value = '{1}';".format(self.loaded_key,
                                                          self.loaded_value))

    def tearDown(self):
        os.environ['espa_api_testing'] = ''
        if os.path.exists(self.bfile):
            os.remove(self.bfile)
        if os.path.exists(self.test_dump):
            os.remove(self.test_dump)

    def test_admin_backup_config(self):
        resp = espa.backup_configuration(self.bfile)
        self.assertTrue(resp)

        self.assertTrue(os.path.exists(self.bfile))

    def test_admin_load_config(self):
        espa.backup_configuration(self.bfile)
        espa.load_configuration(self.test_dump)

        resp = espa.access_configuration(key=self.loaded_key)
        self.assertTrue(self.loaded_value in resp)

        # espa.load_configuration(self.bfile, clear=True)
        # resp = espa.access_configuration(key=self.loaded_key)
        # self.assertIsNone(resp)

        resp = espa.access_configuration(key=self.loaded_key, delete=True)
        self.assertIsNone(resp)

    def test_admin_access_config(self):
        resp = espa.access_configuration(key=self.test_key,
                                         value=self.test_value)
        self.assertTrue(self.test_key in resp)

        resp = espa.access_configuration()
        self.assertTrue(self.test_key in resp)

        resp = espa.access_configuration(key=self.test_key)
        self.assertTrue(self.test_value == resp)

        resp = espa.access_configuration(key=self.test_key, delete=True)
        self.assertIsNone(resp)
