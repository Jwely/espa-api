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
        """
        Create a new scene entry in the ordering_scene table
        Also supports a bulk insert for large sets of scenes to insert
        """
        if isinstance(params, (list, tuple)):
            template = ','.join(['%s'] * len(params))
            args = [(s['name'], s['order_id'], s['status'], s['sensor_type'], s['ee_unit_id'],
                    '', '', '', '', '') for s in params]
        else:
            template = '%s'
            args = (params['name'], params['order_id'], params['status'], params['sensor_type'], params['ee_unit_id'],
                    '', '', '', '', '')

        sql = ("INSERT INTO ordering_scene (name, order_id, status, sensor_type, ee_unit_id, "
               "product_distro_location, product_dload_url, cksum_distro_location, cksum_download_url, "
               "processing_location) VALUES {}".format(template))

        try:
            with DBConnect(**cfg) as db:
                logger.info("scene creation sql: {0}".format(db.cursor.mogrify(sql, args)))
                db.execute(sql, args)
                db.commit()
        except DBConnectException, e:
            raise SceneException("error creating new scene(s): {0}\n sql: {1}\n".format(e.message, sql))

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

    def save(self):
        sql_list = ["UPDATE ordering_scene SET "]
        attr_tup = ('status', 'cksum_download_url', 'log_file_contents', 'processing_location',
                    'retry_after', 'job_name', 'note', 'retry_count', 'sensor_type',
                    'product_dload_url', 'tram_order_id', 'completion_date', 'ee_unit_id',
                    'retry_limit', 'cksum_distro_location', 'product_distro_location')
        date_fields = ('retry_after', 'completion_date')
        for idx, attr in enumerate(attr_tup):
            # dont wrap integer types in quotes
            # tram_order_id is varchar
            if ("_id" in attr or "_limit" in attr or "_count" in attr) and "tram" not in attr:
                sql_snip = "{0} = {1}, "
                quote = False
            else:
                sql_snip = "{0} = '{1}', "
                quote = True

            # lets not insert 'None' into the db
            val = self.__getattribute__(attr)
            if val is None:
                # timestamp fields won't accept empty string
                if attr in date_fields:
                    sql_snip = "{0} = {1}, "
                    val = 'null'
                else:
                    val = "" if quote else 'null'

            # strip the trailing comma 
            if idx == len(attr_tup) - 1:
                sql_snip = sql_snip.replace(",","")

            sql_snip = sql_snip.format(attr, val)
            sql_list.append(sql_snip)

        sql_list.append("WHERE id = {0};".format(self.id))

        sql = " ".join(sql_list)
        logger.info("saving updates to scene {0}\n sql: {1}\n\n".format(self.name, sql))
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
