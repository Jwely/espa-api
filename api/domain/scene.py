""" Holds domain objects for scenes """

from api.util.dbconnect import DBConnectException, db_instance
import psycopg2.extensions as db_extns
from api.system.logger import ilogger as logger
import datetime


class SceneException(Exception):
    pass


class Scene(object):
    """
    Class for interacting with the ordering_scene table
    and holding specific scene information
    """

    base_sql = ('SELECT * '
                'FROM ordering_scene '
                'WHERE ')

    def __init__(self, name=None, note=None, order_id=None,
                 product_distro_location=None, product_dload_url=None,
                 cksum_distro_location=None, cksum_download_url=None,
                 status=None, processing_location=None,
                 completion_date=None, log_file_contents=None,
                 ee_unit_id=None, tram_order_id=None, sensor_type=None,
                 job_name=None, retry_after=None, retry_limit=None,
                 retry_count=None):
        """
        Initialize the Scene object with all the information for it
        from the database

        All parameters are directly related to DB columns

        :param name: scene or collection id
        :param note: text
        :param order_id: ordering_order.id of associated Order
        :param product_distro_location: final location
        :param product_dload_url: access point for users
        :param cksum_distro_location: checksum location
        :param cksum_download_url: access point for users
        :param status: current processing status
        :param processing_location: Hadoop node doing the processing
        :param completion_date: date when processing completed
        :param log_file_contents: Hadoop log file
        :param ee_unit_id: EarthExplorer ID
        :param tram_order_id: LTA tram
        :param sensor_type: landsat/modis/plot
        :param job_name: Hadoop job name
        :param retry_after:
        :param retry_limit:
        :param retry_count:
        :return:
        """

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
            sql = ('select id '
                   'from ordering_scene where '
                   'name = %s '
                   'and order_id = %s')
            db.select(sql, (self.name, self.order_id))

            if db:
                self.id = db[0]['id']
            else:
                self.id = None

    def __repr__(self):
        return 'Scene:{}'.format(self.__dict__)

    @classmethod
    def get(cls, col_name, scene_name, orderid):
        """
        Retrieve a value for a particular column based on
        the long name of the order

        :param col_name: column value to retrieve
        :param scene_name: scene/collection id
        :param orderid: long name for the related order,
         example@somewhere.com-12345
        :return: column value
        """
        sql = ('select %s '
               'from ordering_scene '
               'join ordering_order '
               'on ordering_order.id = ordering_scene.order_id '
               'where ordering_scene.name = %s '
               'and ordering_order.orderid = %s')

        if '.' in col_name:
            _, col = col_name.split('.')
        else:
            col = col_name

        log_sql = ''
        try:
            with db_instance() as db:
                log_sql = (db.cursor.
                           mogrify(sql, (db_extns.AsIs(col_name),
                                         scene_name, orderid)))
                logger.info(log_sql)
                db.select(sql, (db_extns.AsIs(col_name),
                                scene_name, orderid))
                ret = db[0][col]

        except DBConnectException, e:
            logger.debug('err with Scene.get\n'
                         'msg: {0}\n'
                         'sql: {1}'.format(e.message, log_sql))

            raise SceneException(e.message)

        except KeyError, e:
            logger.debug('Scene.get returned no results\n'
                         'sql: {}'.format(log_sql))

            raise SceneException('Key Error: {}'
                                 .format(e.message))

        return ret

    @classmethod
    def create(cls, params):
        """
        Create a new scene entry in the ordering_scene table
        Also supports a bulk insert for large sets of scenes to insert

        dict{'name': ,
             'order_id': ,
             'status': ,
             'sensor_type': ,
             'ee_unit_id': }

        :param params: dictionary representation of a scene to insert
         into the system or a list of dictionary objects
        """
        if isinstance(params, (list, tuple)):
            template = ','.join(['%s'] * len(params))
            args = [(s['name'], s['order_id'],
                     s['status'], s['sensor_type'],
                     s['ee_unit_id'], '', '', '', '', '')
                    for s in params]
        else:
            template = '%s'
            args = [(params['name'], params['order_id'],
                     params['status'], params['sensor_type'],
                     params['ee_unit_id'], '', '', '', '', '')]

        sql = ('INSERT INTO ordering_scene '
               '(name, order_id, status, sensor_type, ee_unit_id, '
               'product_distro_location, product_dload_url, '
               'cksum_distro_location, cksum_download_url, '
               'processing_location) VALUES {}'.format(template))

        try:
            with db_instance() as db:
                logger.info('scene creation sql: {}'
                            .format(db.cursor.mogrify(sql, args)))
                db.execute(sql, args)
                db.commit()

        except DBConnectException, e:
            logger.debug('error creating new scene(s): {}\n'
                         'sql: {}\n'
                         .format(e.message, sql))
            raise SceneException(e.message)

    @classmethod
    def where(cls, params, sql_and=None):
        """
        Query for a particular row in the ordering_scene table

        :param field: columns to select on
        :param value: values of the columns to select on
        :return: list of matching Scene objects
        """
        if not isinstance(params, dict):
            raise SceneException('Where arguments must be'
                                 ' passed as a dictionary')

        fields, values = zip(*params.items())
        fields = ', '.join(fields)

        sql = '{} (%s) = %s'.format(cls.base_sql)

        if sql_and:
            sql += ' AND {}'.format(sql_and)

        ret = []
        with db_instance() as db:
            db.select(sql, (db_extns.AsIs(fields), values))

            for i in db:
                sd = dict(i)
                del sd['id']
                obj = Scene(**sd)
                ret.append(obj)

        return ret

    @classmethod
    def bulk_update(cls, ids=None, updates=None):
        """
        Update a list of scenes with

        :param ids:
        :param updates:
        :return:
        """
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
        """
        Update a specifed column value for this Scene object
        with a new value

        :param att: column to update
        :param val: new value
        :return:
        """
        sql = 'update ordering_scene set %s = %s where id = %s'

        with db_instance() as db:
            db.execute(sql, (db_extns.AsIs(att), val, self.id))
            db.commit()

        self.__setattr__(att, val)

        return self.__getattribute__(att)

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
        logger.info("saving updates to scene {0}\n sql: {1}\n\n".format(self.name, sql))
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
