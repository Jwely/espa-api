import copy

from api.util.dbconnect import db_instance
from api.providers.administration import AdminProviderInterfaceV0, AdministrationProviderException
from api.providers.configuration.configuration_provider import ConfigurationProvider as cp


class AdministrationProvider(AdminProviderInterfaceV0):
    config = cp()
    db = db_instance()

    def orders(self, query=None, cancel=False):
        pass

    def system(self, key=None, disposition='on'):
        pass

    def products(self, query=None, resubmit=None):
        pass

    def configuration(self, key=None, value=None, delete=False):
        if not key:
            return self.config.configuration_keys
        elif not delete and not value:
            return self.config.get(key)
        elif value and not delete:
            return self.config.put(key, value)
        elif value and delete:
            return self.config.delete(key)

    def onlinecache(self, list_orders=False, orderid=None, filename=None, delete=False):
        pass

    def jobs(self, jobid=None, stop=False):
        pass
