""" Holds domain objects for scenes """

from api.dbconnect import DBConnect
from api.utils import api_cfg
cfg = api_cfg()

class Scene(object):

    @classmethod
    def get(cls, value, name=None, order_id=None):
        sql = "select {0} from ordering_scene join ordering_order"\
                " on ordering_order.id = ordering_scene.order_id"\
                " where name = '{1}' and order_id = {2};".format(value, name, order_id)
        print "sql is: %s" % sql
        with DBConnect(**cfg) as db:
            db.select(sql)

        return db[0]



