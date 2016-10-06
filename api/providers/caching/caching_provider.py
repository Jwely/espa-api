from api.providers.caching import CachingProviderInterfaceV0

import memcache


class CachingProviderException(Exception):
    pass


class CachingProvider(CachingProviderInterfaceV0):

    def __init__(self):
        self.cache = memcache.Client(['127.0.0.1:11211'], debug=0)
        self.timeout = 600 # 10 minutes

    def get(self, cache_key):
        return self.cache.get(cache_key)

    def set(self, cache_key, value, expiry=None):
        timeout = expiry or self.timeout
        self.cache.set(cache_key, value, timeout)
        return True

    def delete(self, cache_key):
        self.cache.delete(cache_key)
        return True
