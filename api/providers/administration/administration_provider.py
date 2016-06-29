
from api.util.sshcmd import RemoteHost
from api.providers.administration import AdminProviderInterfaceV0
from api.providers.administration import AdministrationProviderException
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.external.onlinecache import OnlineCache
from api.external.hadoop import HadoopHandler
from api.system.logger import ilogger as logger
from api.util.dbconnect import db_instance
from api.util.dbconnect import DBConnectException


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

    def get_system_status(self):
        sql = "select key, value from ordering_configuration where " \
              "key in ('msg.system_message_body', 'msg.system_message_title', 'system.display_system_message');"
        with db_instance() as db:
            db.select(sql)

        if db:
            resp_dict = dict(db.fetcharr)
            return {'system_message_body': resp_dict['msg.system_message_body'],
                    'system_message_title': resp_dict['msg.system_message_title'],
                    'display_system_message': resp_dict['system.display_system_message']}
        else:
            return {'system_message_body': None, 'system_message_title': None}

    def update_system_status(self, params):

        if params.keys().sort() is not ['system_message_title', 'system_message_body', 'display_system_message'].sort():
            return {'msg': 'Only 3 params are valid, and they must be present: system_message_title, system_message_body, display_system_message'}

        sql_dict = {'msg.system_message_title': params['system_message_title'],
                    'msg.system_message_body': params['system_message_body'],
                    'system.display_system_message': params['display_system_message']}
        sql = ""
        for k, v in sql_dict.iteritems():
            sql += "update ordering_configuration set value = '{0}' where key = '{1}';".format(v, k)

        try:
            with db_instance() as db:
                db.execute(sql)
                db.commit()
        except DBConnectException as e:
            logger.debug("error updating system status: {}".format(e))
            return {'msg': "error updating database: {}".format(e.message)}

        return True

    def get_system_config(self):
        return ConfigurationProvider()._retrieve_config()
