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
        return 'Scene: {}'.format(self.__dict__)

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

        except DBConnectException as e:
            logger.debug('Error scene get\n'
                         'msg: {0}\n'
                         'sql: {1}'.format(e.message, log_sql))

            raise SceneException(e.message)

        except KeyError as e:
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

        log_sql = ''
        try:
            with db_instance() as db:
                log_sql = db.cursor.mogrify(sql, args)
                logger.info('scene creation sql: {}'
                            .format(log_sql))
                db.execute(sql, args)
                db.commit()

        except DBConnectException as e:
            logger.debug('error creating new scene(s): {}\n'
                         'sql: {}\n'
                         .format(e.message, log_sql))
            raise SceneException(e.message)

    @classmethod
    def where(cls, params, sql_and=None):
        """
        Query for a particular row in the ordering_scene table

        :param params: dictionary of column: value parameter to select on
        :param sql_and: custom query parameter for anything besides =
        :return: list of matching Scene objects
        """
        if not isinstance(params, dict):
            raise SceneException('Where arguments must be '
                                 'passed as a dictionary')

        fields, values = zip(*params.items())
        fields = ', '.join(fields)

        sql = '{} (%s) = %s'.format(cls.base_sql)

        if sql_and:
            sql += ' AND {}'.format(sql_and)

        ret = []
        log_sql = ''
        try:
            with db_instance() as db:
                log_sql = db.cursor.mogrify(sql, (db_extns.AsIs(fields),
                                                  values))
                logger.info('scene.py where sql: {}'.format(log_sql))

                db.select(sql, (db_extns.AsIs(fields), values))

                for i in db:
                    sd = dict(i)
                    del sd['id']
                    obj = Scene(**sd)
                    ret.append(obj)
        except DBConnectException as e:
            logger.debug('Error retrieving scenes: {}\n'
                         'sql: {}'.format(e.message, log_sql))
            raise SceneException(e)

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
            raise TypeError('Scene.bulk_update ids should be a list')
        if not isinstance(updates, dict):
            raise TypeError('Scene.bulk_update updates should be a dict')

        sql = 'UPDATE ordering_scene SET %s = %s WHERE id in %s'

        fields = '({})'.format(','.join(updates.keys()))
        vals = tuple(updates.values())
        ids = tuple(ids)

        if ",)" in sql:
            sql = sql.replace(",)", ")")

        log_sql = ''
        try:
            with db_instance() as db:
                log_sql = db.cursor.mogrify(sql, (db_extns.AsIs(fields),
                                                  vals, ids))
                logger.info(log_sql)
                db.execute(sql, (db_extns.AsIs(fields), vals, ids))
                db.commit()
        except DBConnectException as e:
            logger.debug('Error scene bulk_update: {}\nSQL: {}'
                         .format(e.message, log_sql))
            raise SceneException(e)

        return True

    def update(self, att, val):
        """
        Update a specifed column value for this Scene object
        with a new value

        :param att: column to update
        :param val: new value
        :return: updated value from self
        """
        sql = 'update ordering_scene set %s = %s where id = %s'

        log_sql = ''
        try:
            with db_instance() as db:
                log_sql = db.cursor.mogrify(sql, (db_extns.AsIs(att),
                                                  val, self.id))
                logger.info(log_sql)
                db.execute(sql, (db_extns.AsIs(att), val, self.id))
                db.commit()
        except DBConnectException as e:
            logger.debug('Error updating scene: {}\nSQL: {}'
                         .format(e.message, log_sql))

        self.__setattr__(att, val)

        return self.__getattribute__(att)

    def save(self):
        """
        Save the current configuration of the scene object to the DB
        """
        sql = 'UPDATE ordering_scene SET %s = %s WHERE id = %s'

        attr_tup = ('status', 'cksum_download_url', 'log_file_contents',
                    'processing_location', 'retry_after', 'job_name',
                    'note', 'retry_count', 'sensor_type',
                    'product_dload_url', 'tram_order_id',
                    'completion_date', 'ee_unit_id', 'retry_limit',
                    'cksum_distro_location', 'product_distro_location')

        vals = tuple(self.__getattribute__(v) for v in attr_tup)
        cols = '({})'.format(','.join(attr_tup))

        log_sql = ''
        try:
            with db_instance() as db:
                log_sql = db.cursor.mogrify(sql, (db_extns.AsIs(cols),
                                                  vals, self.id))

                db.execute(sql, (db_extns.AsIs(cols), vals, self.id))
                db.commit()
                logger.info('Saved updates to scene id: {}, name:{}\n'
                            'sql: {}\n args: {}\n'
                            .format(self.id, self.name,
                                    log_sql, zip(attr_tup, vals)))
        except DBConnectException as e:
            logger.debug("Error saving scene: {}\n"
                         "sql: {}".format(e.message, log_sql))
            raise SceneException(e)

        new = Scene.where({'id': self.id})[0]

        for att in attr_tup:
            self.__setattr__(att, new.__getattribute__(att))

    def order_attr(self, col):
        """
        Select the column value from the ordering_order table for this
        specific scene

        :param col: column to select on
        :return: value
        """
        sql = ('SELECT %s '
               'FROM ordering_scene JOIN ordering_order '
               'ON ordering_order.id = ordering_scene.order_id '
               'WHERE name = %s')

        log_sql = ''
        try:
            with db_instance() as db:
                log_sql = db.cursor.mogrify(sql, (db_extns.AsIs(col),
                                                  self.name))
                db.select(sql, (db_extns.AsIs(col), self.name))
                ret = db[0][col]

        except DBConnectException as e:
            logger.debug('Error retrieving order_attr: {}\n'
                         'sql: {} \n'.format(e.message, log_sql))
            raise SceneException(e)

        except KeyError as e:
            logger.debug('Error order_attr returned no results\n'
                         'sql: {}'.format(log_sql))

            raise SceneException('Key Error: {}'
                                 .format(e.message))

        return ret
