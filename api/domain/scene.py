""" Holds domain objects for scenes """

from api.util.dbconnect import DBConnectException, db_instance
import psycopg2.extensions as db_extns
from api.system.logger import ilogger as logger
import datetime

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
        with db_instance() as db:
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
            with db_instance() as db:
                db.select(sql)
            return db[0][value]
        except DBConnectException, e:
            logger.debug("err with Scene.get, \nmsg: {0}\nsql: {1}".format(e.message, sql))
            raise SceneException(e.message)

    @classmethod
    def create(cls, params):
        """
        Create a new scene entry in the ordering_scene table
        Also supports a bulk insert for large sets of scenes to insert

        :param params: dictionary representation of a scene to insert into the system
                       or a list of dictionary objects
        """
        if isinstance(params, (list, tuple)):
            template = ','.join(['%s'] * len(params))
            args = [(s['name'], s['order_id'], s['status'], s['sensor_type'], s['ee_unit_id'],
                    '', '', '', '', '') for s in params]
        else:
            template = '%s'
            args = [(params['name'], params['order_id'], params['status'], params['sensor_type'], params['ee_unit_id'],
                    '', '', '', '', '')]

        sql = ("INSERT INTO ordering_scene "
               "(name, order_id, status, sensor_type, ee_unit_id, "
               "product_distro_location, product_dload_url, "
               "cksum_distro_location, cksum_download_url, "
               "processing_location) VALUES {}".format(template))

        try:
            with db_instance() as db:
                logger.info("scene creation sql: {0}".format(db.cursor.mogrify(sql, args)))
                db.execute(sql, args)
                db.commit()
        except DBConnectException, e:
            raise SceneException("error creating new scene(s): {0}\n sql: {1}\n".format(e.message, sql))

        # scene = Scene.where("name = '{0}' AND order_id = {1}".format(params['name'], params['order_id']))[0]
        return True

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
        sql = sql.replace(",)", ")")
        with db_instance() as db:
            db.select(sql)
            returnlist = []
            for i in db:
                sd = dict(i)
                del sd["id"]
                obj = Scene(**sd)
                returnlist.append(obj)

        return returnlist

    @classmethod
    def bulk_update(cls, ids=None, updates=None):
        if not ids:
            ids = ()
        if not updates:
            updates = {}

        if not isinstance(ids, (list, tuple)):
            raise TypeError("Scene.bulk_update ids should be a list")
        if not isinstance(updates, dict):
            raise TypeError("Scene.bulk_update updates should be a dict")

        sql = 'UPDATE ordering_scene SET %s = %s WHERE id in %s'

        fields = '({})'.format(','.join(updates.keys()))
        vals = tuple(updates.values())
        ids = tuple(ids)

        if ",)" in sql:
            sql = sql.replace(",)", ")")

        try:
            with db_instance() as db:
                logger.info(db.cursor.mogrify(sql, (db_extns.AsIs(fields), vals, ids)))
                db.execute(sql, (db_extns.AsIs(fields), vals, ids))
                db.commit()
        except DBConnectException, e:
            raise SceneException(e.message)

        return True

    def update(self, att, val):
        self.__setattr__(att, val)
        if isinstance(val, str) or isinstance(val, datetime.datetime):
            val = "\'{0}\'".format(val)
        sql = "update ordering_scene set {0} = {1} where id = {2};".format(att, val, self.id)
        with db_instance() as db:
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
        arg_list = []
        for idx, attr in enumerate(attr_tup):
            sql_snip = "{0} = %s, "
            val = self.__getattribute__(attr)

            # strip the trailing comma 
            if idx == len(attr_tup) - 1:
                sql_snip = sql_snip.replace(",","")

            sql_snip = sql_snip.format(attr)
            sql_list.append(sql_snip)
            arg_list.append(val)

        sql_list.append("WHERE id = {0};".format(self.id))

        sql = " ".join(sql_list)
        logger.info("saving updates to scene id:{0}, name:{1}\n sql: {2}\n args: {3}\n".format(self.id, self.name, sql, arg_list))
        try:
            with db_instance() as db:
                db.execute(sql, arg_list)
                db.commit()
                return True
        except DBConnectException, e:
            logger.debug("ERROR saving scene. msg: {0}\nsql: {1}".format(e.message, sql))
            raise SceneException(e.message)

    def order_attr(self, att):
        sql = "select {0} from ordering_scene join ordering_order "\
                "on ordering_order.id = ordering_scene.order_id "\
                "where name = '{1}';".format(att, self.name)
        try:
            with db_instance() as db:
                db.select(sql)
            return db[0][att]
        except DBConnectException as e:
            logger.debug("err with Scene.get, \nmsg: {0}\nsql: {1} \n".format(e.message, sql))
            raise SceneException(e)
