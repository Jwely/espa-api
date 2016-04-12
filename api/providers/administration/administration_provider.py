import copy

from api.util.dbconnect import db_instance
from api.util.sshcmd import RemoteHost
from api.providers.administration import AdminProviderInterfaceV0, AdministrationProviderException
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.external.onlinecache import OnlineCache


class AdministrationProvider(AdminProviderInterfaceV0):
    config = ConfigurationProvider()
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
        elif delete:
            return self.config.delete(key)

    def onlinecache(self, list_orders=False, orderid=None, filename=None, delete=False):
        if delete and orderid and filename:
            return OnlineCache().delete(orderid, filename)
        elif delete and orderid:
            return OnlineCache().delete(orderid)
        elif list_orders:
            return OnlineCache().list()
        elif orderid:
            return OnlineCache().list(orderid)
        else:
            return OnlineCache().capacity()

    def jobs(self, jobid=None, stop=False):
        params = ('hadoop.master',
                  'landsatds.username',
                  'landsatds.password')

        vals = self.config.get(params)

        remote = RemoteHost(host=vals[0], user=vals[1], pw=vals[2])

        command = 'some bash script command'

        resp = remote.execute(command)

        return resp
