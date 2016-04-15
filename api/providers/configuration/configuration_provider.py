import os
import datetime

from api.util.dbconnect import db_instance
from api.providers.configuration import ConfigurationProviderInterfaceV0


class ConfigurationProviderException(Exception):
    pass


class ConfigurationProvider(ConfigurationProviderInterfaceV0):
    @property
    def mode(self):
        apimode = 'dev'

        if 'ESPA_ENV' in os.environ.keys():
            apimode = os.environ['ESPA_ENV']

        if apimode not in ['dev', 'tst', 'ops']:
            raise ConfigurationProviderException('Invalid environment value for ESPA_ENV: {0}'.format(apimode))

        return apimode

    @property
    def configuration_keys(self):
        return self._retrieve_config()

    def url_for(self, service_name):
        key = "url.{0}.{1}".format(self.mode, service_name)
        current = self._retrieve_config()

        return current.get(key)

    def get(self, key):
        current = self._retrieve_config()

        if isinstance(key, (list, tuple)):
            ret = [current.get(k) for k in key]
        else:
            ret = current.get(key)

        if 'apiemailreceive' in key and os.environ.get('apiemailreceive'):
            if isinstance(ret, list):
                idx = key.index('apiemailreceive')
                ret[idx] = os.environ['apiemailreceive']
            else:
                ret = os.environ['apiemailreceive']

        if isinstance(ret, list):
            return tuple(ret)
        else:
            return ret

    def put(self, key, value):
        self.dump()

        query = ('insert into ordering_configuration (key, value) values (%s, %s) '
                 'on conflict (key) '
                 'do update set value = %s')

        with db_instance() as db:
            db.execute(query, (key, value, value))
            db.commit()

        return {key: self.get(key)}

    def delete(self, key):
        self.dump()

        if self.exists(key):
            query = 'delete from ordering_configuration where key = %s'

            with db_instance() as db:
                db.execute(query, (key,))
                db.commit()

        return self.get(key)

    def exists(self, key):
        current = self._retrieve_config()

        if key in current:
            return True
        else:
            return False

    def load(self, path, clear=False):
        self.dump()

        if clear:
            with db_instance() as db:
                db.execute('TRUNCATE ordering_configuration')
                db.commit()

        with open(path, 'r') as f:
            sql = f.read()

        with db_instance() as db:
            db.execute(sql)
            db.commit()

    def dump(self, path=None):
        ts = datetime.datetime.now().strftime('config-%m%d%y-%H%M%S')

        if not path:
            base = os.path.join(os.path.expanduser('~'), '.usgs', '.config_backup')
            if not os.path.exists(base):
                os.makedirs(base)

            path = os.path.join(base, ts)

        current = self._retrieve_config()
        line = ("INSERT INTO orderding_configuration (key, value) VALUES ('{0}', '{1}') "
                "on conflict (key) "
                "do update set value = '{1}';\n")

        with open(path, 'w') as f:
            for key, value in current.items():
                f.write(line.format(key, value))

        return os.path.exists(path)

    @staticmethod
    def _retrieve_config():
        config = {}
        with db_instance() as db:
            con_query = 'select key, value from ordering_configuration'
            db.select(con_query)
            for i in db:
                config[i['key']] = i['value']

        return config
