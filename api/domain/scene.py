""" Holds domain objects for scenes """

from api.dbconnect import DBConnect, DBConnectException
from api.api_logging import api_logger as logger
from api.utils import api_cfg
cfg = api_cfg()

class SceneException(Exception):
    pass

class Scene(object):

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


