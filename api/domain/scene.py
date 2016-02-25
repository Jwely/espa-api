""" Holds domain objects for scenes """

from api.dbconnect import DBConnect, DBConnectException
from api.api_logging import api_logger as logger
from api.utils import api_cfg
import datetime
cfg = api_cfg()

class SceneException(Exception):
    pass

class Scene(object):
    """ Class for interacting with the ordering_scene table """

    base_sql = "SELECT id, name, note, order_id, product_distro_location, product_dload_url,"\
                " cksum_distro_location, cksum_download_url, status, processing_location,"\
                " completion_date, log_file_contents, ee_unit_id, tram_order_id,"\
                " sensor_type, job_name, retry_after, retry_limit, retry_count FROM"\
                " ordering_scene WHERE "

    def __init__(self, atts):
        for key, value in atts.iteritems():
            setattr(self, key, value)

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
    def create(cls, params):
        sql = "INSERT INTO ordering_scene (name, order_id, status, sensor_type, ee_unit_id, "\
                "product_distro_location, product_dload_url, cksum_distro_location, cksum_download_url, "\
                "processing_location) VALUES ('{0}',{1},'{2}','{3}',{4},'','','','','');".format(
                    params['name'],params['order_id'],params['status'],params['sensor_type'],
                    params['ee_unit_id'])

        logger.info("scene creation sql: {0}".format(sql))
        try:
            with DBConnect(**cfg) as db:
                db.execute(sql)
                db.commit()
        except DBConnectException, e:
            raise SceneException("error creating new scene: {0}\n sql: {1}\n".format(e.message, sql))

        scene = Scene.where("name = '{0}' AND order_id = {1}".format(params['name'], params['order_id']))[0]
        return scene

    @classmethod
    def where(cls, params):
        sql = [str(cls.base_sql)]
        if isinstance(params, list):
            param_str = " AND ".join(params)
            sql.append(param_str)
        elif isinstance(params, str):
            sql.append(params)
        else:
            raise SceneException("Scene.where arg needs to be a list or a str")

        sql.append(";")
        sql = " ".join(sql)
        with DBConnect(**cfg) as db:
            db.select(sql)
            returnlist = []
            for i in db:
                obj = Scene(i)
                returnlist.append(obj)

        return returnlist

    def update(self, att, val):
        self.__setattr__(att, val)
        if isinstance(val, str) or isinstance(val, datetime.datetime):
            val = "\'{0}\'".format(val)
        sql = "update ordering_scene set {0} = {1} where id = {2};".format(att, val, self.id)
        with DBConnect(**cfg) as db:
            db.execute(sql)
            db.commit()
        return True

    def order_attr(self, att):
        sql = "select {0} from ordering_scene join ordering_order "\
                "on ordering_order.id = ordering_scene.order_id "\
                "where name = '{1}';".format(att, self.name)
        try:
            with DBConnect(**cfg) as db:
                db.select(sql)
            return db[0][att]
        except DBConnectException as e:
            logger.debug("err with Scene.get, \nmsg: {0}\nsql: {1} \n".format(e.message, sql))
            raise SceneException(e)
