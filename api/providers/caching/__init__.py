import abc

import memcache

class CachingInterfaceV0(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get(self, key):
        """
        Retrieve an item from the cache based on key

        :param key: key to an associated object
        :return: object
        """

    @abc.abstractmethod
    def set(self, key, value, expirey=None):
        """
        Place an item into the cache

        :param key: identifying key to the stored object
        :param value: object to store in the cache
        :param expirey: time in seconds an object will live in the cache
        :return: True if successful, else False
        """


class CachingProvider(CachingInterfaceV0, memcache.Client):
    def __init__(self, server, *args, **kwargs):
        super(CachingProvider, self).__init__(server, *args, **kwargs)
