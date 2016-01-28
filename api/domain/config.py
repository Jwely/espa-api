"""
Purpose: serve up settings stored
on the configuration table
"""

from api.utils import get_cfg
from api.dbconnect import DBConnect
import psycopg2.extras

class ApiConfig(object):
    """
    Object for serving up settings
    stored in the database
    """

    def __init__(self, cfgfile=None):

        cfgout = {}

        if cfgfile is None:
            cfg = get_cfg()['config']
        else:
            cfg = get_cfg(cfgfile)['config']

        cfg['cursor_factory'] = psycopg2.extras.DictCursor



        with DBConnect(**cfg) as db:
            con_query = "select key, value from ordering_configuration;"
            db.select(con_query)
            for i in db:
                cfgout[i['key']] = i['value']

        self.cfg = cfg
        self.settings = cfgout

    def mode(self):
        apimode = 'dev'
        if self.cfg['dbuser'] == 'espa':
            apimode = 'ops'
        elif self.cfg['dbuser'] == 'espatst':
            apimode = 'tst'

        return apimode

    def service_name_url(self):
        key = "url.%s.registration" % self.mode()
        return self.settings[key]



























