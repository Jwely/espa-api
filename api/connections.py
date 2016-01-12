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

class ApiDB(object):
    def __init__(self):
        cfg = os.environ.get('ESPA_CONFIG_FILE', 
                os.path.join(os.path.expanduser('~'), '.cfgnfo'))

        if os.path.isfile(cfg):
            conf = open(cfg)
            conn = conf.read()
            conf.close()
            details = dictize(conn)
        else:
            # raise exception
            pass

        posthost = details['post-host']
        postport = details['post-port']
        postuser = details['post-user']
        postpass = details['post-pass']
        postdb = details['post-db']
