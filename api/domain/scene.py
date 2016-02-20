""" Holds domain objects for scenes """

from api.dbconnect import DBConnect, DBConnectException
from api.api_logging import api_logger as logger
from api.utils import api_cfg
cfg = api_cfg()

class SceneException(Exception):
    pass

class Scene(object):
    """ Class for interacting with the ordering_scene table """

    def __init__(self, oid):
        """
        Args:
        id (int): primary key for the order to be retrieved
        """
        obj = None
        with DBConnect(**cfg) as db:
            sql = "select * from ordering_scene where id = {0};".format(oid)
            db.select(sql)
            obj = db[0]

        for k, v in obj.iteritems():
            setattr(self, k, v)

    def __repr__(self):
        return "Scene:{0}".format(self.__dict__)

    @classmethod
    def get(cls, value, name=None, orderid=None):
        sql = "select {0} from ordering_scene join ordering_order"\
                " on ordering_order.id = ordering_scene.order_id"\
                " where name = '{1}' and orderid = '{2}';".format(value, name, orderid)
        try:
            with DBConnect(**cfg) as db:
                db.select(sql)
            return db[0][value]
        except DBConnectException as e:
            logger.debug("err with Scene.get, \nmsg: {0}\nsql: {1} \n".format(e.message, sql))
            raise SceneException(e)

    @classmethod
    def where(cls, att=None, val=None):
        sql = "select id from ordering_scene where {0} = "
        if isinstance(val, str):
            sql += "'{1}';"
        else:
            sql += "{1};"
        sql = sql.format(att, val)
        with DBConnect(**cfg) as db:
            db.select(sql)
            returnlist = []
            for i in db:
                obj = Scene(i['id'])
                returnlist.append(obj)

        return returnlist
