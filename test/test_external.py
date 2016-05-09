import unittest
from mock import patch

from api.external.nlaps import products_are_nlaps
from api.external import onlinecache
from api.external.mocks import onlinecache as mockonlinecache


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


# class TestOnlineCache(unittest.TestCase):
#     """
#     Tests for dealing with the distribution cache
#     """
#     def setUp(self):
#         self.cache = onlinecache.OnlineCache()
#
#     def test_cache_listorders(self):
#         results = self.cache.list()
#
#         self.assertTrue(results)
#
#     def test_cache_capcity(self):
#         results = self.cache.capacity()
#
#         self.assertTrue('capacity' in results)
#
#     @patch('api.external.onlinecache.OnlineCache.delete', mockonlinecache.delete)
#     def test_cache_deleteorder(self):
#         results = self.cache.delete('bilbo')
#         self.assertTrue(results)
