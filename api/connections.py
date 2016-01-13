""" Object for interacting with the database """

import sys, os
import psycopg2

def dictize(instring):
    output = {}
    inl = instring.split("\n")
    for item in inl:
        if "=" in item:
            i = item.split("=")
            output[i[0]] = i[1]
    return output

class ConnectionError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class ApiDB(object):
    def __init__(self):
        cfg = os.environ.get('ESPA_CONFIG_FILE',
                os.path.join(os.path.expanduser('~'), '.cfgnfo'))

        try:
            with open(cfg, 'r') as f:
                conf = f.read()

            details = dictize(conf)
            posthost = details['post-host']
            postport = details['post-port']
            postuser = details['post-user']
            postpass = details['post-pass']
            postdb = details['post-db']
            conn_str = "dbname='%s' user='%s' host='%s' password='%s'" % (postdb, postuser, posthost, postpass)

            try:
                conn = psycopg2.connect(conn_str)
            except psycopg2.OperationalError, err:
                raise psycopg2.OperationalError(err)

        except IOError, err:
            raise IOError(' cant open file %s - %s' % (cfg, err))




