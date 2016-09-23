import unittest
from mock import patch

from api.external.nlaps import products_are_nlaps
from api.external import onlinecache
from api.external.mocks import onlinecache as mockonlinecache
from api.external import lta
from api.external.mocks import lta as mocklta
from api.external.hadoop import HadoopHandler


class TestLTA(unittest.TestCase):
    def setUp(self):
        pass

    def test_verify_scenes(self):
        pass
        #product_list = ['LT50300372011275PAC01','LE70280312004362EDC00']
        #resp = lta.verify_scenes(product_list)
        #for item in product_list:
        #    self.assertTrue(item in resp.keys())
        #    self.assertTrue(resp[item])

    @patch('api.external.lta.OrderUpdateServiceClient.update_order', mocklta.return_update_order_resp)
    #@patch('api.external.lta.SoapClient.getAvailableOrders', mocklta.get_available_orders)
    def test_get_available_orders(self):
        pass
        #resp = lta.get_available_orders()
        #print resp


class TestNLAPS(unittest.TestCase):
    """
    Provide testing for sorting out NLAPS products
    """
    def setUp(self):
        self.nlaps = ['LT40150231982306AAA02',
                      'LT40360241982341AAA05',
                      'LT51392101985039AAA03',
                      'LT51790261985079AAA04',
                      'LT50460331985171AAA04']

        self.non_nlaps = ['LT50290302011300PAC01',
                          'LC80300302016065LGN00',
                          'LE70300302016057EDC00',
                          'LE70290302003126EDC00']

    def test_nlaps_prods(self):
        all = [_ for _ in self.nlaps]
        all.extend(self.non_nlaps)

        nlaps_prods = products_are_nlaps(all)

        for prod in nlaps_prods:
            self.assertTrue(prod in self.nlaps)
            self.assertTrue(prod not in self.non_nlaps)


class TestOnlineCache(unittest.TestCase):
    """
    Tests for dealing with the distribution cache
    """
    def setUp(self):
        self.cache = onlinecache.OnlineCache()

    def test_cache_listorders(self):
        results = self.cache.list()

        self.assertTrue(results)

    def test_cache_capcity(self):
        results = self.cache.capacity()

        self.assertTrue('capacity' in results)

    @patch('api.external.onlinecache.OnlineCache.delete', mockonlinecache.delete)
    def test_cache_deleteorder(self):
        results = self.cache.delete('bilbo')
        self.assertTrue(results)


class TestHadoopHandler(unittest.TestCase):
    """
    Tests for the hadoop interaction class
    """
    def setUp(self):
        self.hadoop = HadoopHandler()

    def test_list_jobs(self):
        resp = self.hadoop.list_jobs()
        self.assertTrue('stdout' in resp.keys())

    def test_job_names_ids(self):
        resp = self.hadoop.job_names_ids()
        self.assertTrue(isinstance(resp, dict))

    def test_slave_ips(self):
        resp = self.hadoop.slave_ips()
        self.assertTrue(isinstance(resp, list))
        self.assertTrue(len(resp) > 0)

    def test_master_ip(self):
        resp = self.hadoop.master_ip()
        self.assertTrue(isinstance(resp, str))
        self.assertTrue(len(resp.split('.')) == 4)
