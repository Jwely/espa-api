"""
Purpose: serve up settings stored
on the configuration table
"""

from api.domain.utils import api_cfg
from api.domain.dbconnect import DBConnect
import psycopg2.extras

class ApiConfig(object):
    """
    Object for serving up settings
    stored in the database
    """

    def __init__(self, cfgfile=None):

        cfgout = {}

        if cfgfile is None:
            cfg = api_cfg()
        else:
            cfg = api_cfg(cfgfile)

        with DBConnect(**cfg) as db:
            con_query = "select key, value from ordering_configuration;"
            db.select(con_query)
            for i in db:
                cfgout[i['key']] = i['value']

        self.cfg = cfg
        self.settings = cfgout

    @property
    def mode(self):
        apimode = 'dev'
        if self.cfg['dbuser'] == 'espa':
            apimode = 'ops'
        elif self.cfg['dbuser'] == 'espatst':
            apimode = 'tst'

        return apimode

    def url_for(self, service_name):
        key = "url.{0}.{1}".format(self.mode, service_name)
        return self.settings[key]

