import copy

from api.util.dbconnect import db_instance
from api.util.sshcmd import RemoteHost
from api.providers.administration import AdminProviderInterfaceV0, AdministrationProviderException
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.external.onlinecache import OnlineCache
from api.external.hadoop import HadoopHandler


class AdministrationProvider(AdminProviderInterfaceV0):
    config = ConfigurationProvider()
    db = db_instance()

    def orders(self, query=None, cancel=False):
        pass

    def system(self, key=None, disposition='on'):
        pass

    def products(self, query=None, resubmit=None):
        pass

    def access_configuration(self, key=None, value=None, delete=False):
        if not key:
            return self.config.configuration_keys
        elif not delete and not value:
            return self.config.get(key)
        elif value and not delete:
            return self.config.put(key, value)
        elif delete and key:
            return self.config.delete(key)

    # def restore_configuration(self, filepath, clear=False):
    def restore_configuration(self, filepath):
        # self.config.load(filepath, clear=clear)
        self.config.load(filepath)

    def backup_configuration(self, path=None):
        return self.config.dump(path)

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
        if not jobid:
            resp = HadoopHandler().list_jobs()
        else:
            resp = HadoopHandler().kill_job(jobid)

        return resp
