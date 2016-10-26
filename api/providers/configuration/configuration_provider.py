import os
import datetime
import yaml

from api.util.dbconnect import db_instance
from api.providers.configuration import ConfigurationProviderInterfaceV0
from api.util import api_cfg


class ConfigurationProviderException(Exception):
    pass


class ConfigurationProvider(ConfigurationProviderInterfaceV0):

    def __init__(self):
        # fetch vars set in api_cfg['config']
        for k, v in api_cfg().iteritems():
            self.__setattr__(k, v)

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

    # def load(self, path, clear=False):
    def load(self, path):
        self.dump()

        # Debating the merits of such an operation
        # if clear:
        #     with db_instance() as db:
        #         db.execute('DELETE FROM ordering_configuration')
        #         db.commit()

        with open(path, 'r') as f:
            sql = f.read()

        with db_instance() as db:
            db.execute(sql)
            db.commit()

    def dump(self, path=None):
        ts = datetime.datetime.now().strftime('config-%m%d%y-%H%M%S')

        if not path:
            base = os.path.join(os.environ['ESPA_CONFIG_PATH'], '.usgs', '.config_backup')
            if not os.path.exists(base):
                os.makedirs(base)

            path = os.path.join(base, ts)

        current = self._retrieve_config()
        line = ("INSERT INTO ordering_configuration (key, value) VALUES ('{0}', '{1}') "
                "ON CONFLICT (key) "
                "DO UPDATE SET value = '{1}';\n")

        with open(path, 'w') as f:
            for key, value in current.items():
                f.write(line.format(key, value))

        return path

    def switch_ee_environment(self, environment):
        if environment not in ('dev', 'tst', 'ops'):
            raise ConfigurationProviderException('invalid argument value for switch_ee_environment')

        print "****\nWARNING:\nSwitching backend EE/LTA service environments " \
              "from {} to {}\n****\n".format(self.mode, environment)

        def up_vals(key, val):
            print key + ' to: ' + val
            resp = self.put(key, val)
            if resp == {_up_key: _up_val}:
                print 'update successful'
            else:
                print 'there was a problem, return value was: {}'.format(_resp)

        try:
            with open(self.explorer_yaml) as f:
                _edict = yaml.load(f.read())

            for grp in _edict:
                for key in _edict[grp]:
                    if '_urls' in grp:
                        _up_key = 'url.' + self.mode + '.' + key
                    else:
                        _kl = key.split('_')
                        _up_key = '.'.join((_kl[0], self.mode, _kl[1]))
                    _up_val = _edict[grp][key][environment]
                    up_vals(_up_key, _up_val)
            return True
        except AttributeError as e:
            raise ConfigurationProviderException("explorer_yaml not defined in .cfgnfo")
        except IOError as e:
            raise ConfigurationProviderException("{} as defined by explorer_yaml in "
                                                 ".cfgnfo not found".format(self.explorer_yaml))

    @staticmethod
    def _retrieve_config():
        config = {}
        with db_instance() as db:
            con_query = 'select key, value from ordering_configuration'
            db.select(con_query)
            for i in db:
                config[i['key']] = i['value']

        return config
