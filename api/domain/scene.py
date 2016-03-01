""" Holds domain objects for scenes """

from api.domain.dbconnect import DBConnect, DBConnectException
from api.api_logging import api_logger as logger
from api.domain.utils import api_cfg
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

    def __init__(self, name=None, note=None, order_id=None, product_distro_location=None,
                product_dload_url=None, cksum_distro_location=None, cksum_download_url=None,
                status=None, processing_location=None, completion_date=None,
                log_file_contents=None, ee_unit_id=None, tram_order_id=None,
                sensor_type=None, job_name=None, retry_after=None, retry_limit=None,
                retry_count=None):
        self.name = name
        self.note = note
        self.order_id = order_id
        self.product_distro_location = product_distro_location
        self.product_dload_url= product_dload_url
        self.cksum_distro_location = cksum_distro_location
        self.cksum_download_url = cksum_download_url
        self.status = status
        self.processing_location = processing_location
        self.completion_date = completion_date
        self.log_file_contents = log_file_contents
        self.ee_unit_id = ee_unit_id
        self.tram_order_id = tram_order_id
        self.sensor_type = sensor_type
        self.job_name = job_name
        self.retry_after = retry_after
        self.retry_limit = retry_limit
        self.retry_count = retry_count
        with DBConnect(**cfg) as db:
            sql = "select id from ordering_scene where "\
                    "name = '{0}' and order_id = {1};".format(self.name, self.order_id)
            db.select(sql)
            if db:
                self.id = db[0]['id']
            else:
                self.id = None

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
                sd = dict(i)
                del sd["id"]
                obj = Scene(**sd)
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
