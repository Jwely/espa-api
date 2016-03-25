import os
from api.util.dbconnect import db_instance
from api.providers.configuration import ConfigurationProviderInterfaceV0
from api.util import api_cfg

class ConfigurationProviderException(Exception):
    pass

class ConfigurationProvider(ConfigurationProviderInterfaceV0):

    def __init__(self):
        cfgout = {}
        with db_instance() as db:
            con_query = "select key, value from ordering_configuration;"
            db.select(con_query)
            for i in db:
                cfgout[i['key']] = i['value']

        self.settings = cfgout
        for k, v in api_cfg().iteritems():
            self.__setattr__(k, v)

        self.db_creds = api_cfg('db')


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
        return self.settings.keys()

    def url_for(self, service_name):
        key = "url.{0}.{1}".format(self.mode, service_name)
        return self.settings[key]

    def get(self, key):
        val = self.settings[key]
        if key is 'apiemailreceive' and 'apiemailreceive' in os.environ.keys():
            val = os.environ['apiemailreceive']
        return val

    def put(self, key, value):
        raise NotImplementedError

    def mget(self, keys):
        raise NotImplementedError

    def mput(self, kv_dict):
        raise NotImplementedError

    def mdelete(self, keys):
        raise NotImplementedError

    def exists(self, key):
        raise NotImplementedError

    def load(self, config):
        raise NotImplementedError

    def dump(self, path):
        raise NotImplementedError


