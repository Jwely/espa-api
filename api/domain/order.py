""" Holds domain objects for orders and the items attached to them """

from api.utils import api_cfg
from api.dbconnect import DBConnect
from api.domain.scene import Scene
from api.api_logging import api_logger as logger
from psycopg2.extras import Json
import datetime

cfg = api_cfg()

class OrderException(Exception):
    pass

class Order(object):
    """ Class for interacting with the ordering_order table """

    base_sql = "SELECT id, orderid, email, order_date, status, product_options,"\
                "order_source, ee_order_id, user_id, order_type, priority,"\
                "completion_date, note, initial_email_sent,"\
                "completion_email_sent, product_opts FROM ordering_order WHERE "

    def __init__(self, atts):
        for key, value in atts.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return "Order:{0}".format(self.__dict__)

    @classmethod
    def create(cls, params):
        sql = "INSERT INTO ordering_order (orderid, user_id, order_type, status,"\
                "note, product_opts, ee_order_id, order_source, order_date, "\
                "priority) VALUES ('{0}',{1},'{2}','{3}','{4}','{5}',{6},"\
                "'{7}','{8}','{9}');".format(params['orderid'],params['user_id'],params['order_type'],
                                                params['status'],params['note'],params['product_opts'],
                                                params['ee_order_id'],params['order_source'],params['order_date'],
                                                params['priority'] )

        logger.info("order creation sql: {0}".format(sql))

        try:
            with DBConnect(**cfg) as db:
                db.execute(sql)
                db.commit()
        except DBConnectException, e:
            raise OrderException("error creating new order: {0}\n sql: {1}\n".format(e.message, sql))

        order = Order.where("orderid = '{0}'".format(params['orderid']))[0]
        return order

    @classmethod
    def where(cls, params):
        sql = [str(cls.base_sql)]
        if isinstance(params, list):
            param_str = " AND ".join(params)
            sql.append(param_str)
        elif isinstance(params, str):
            sql.append(params)
        else:
            raise OrderException("Order.where arg needs to be a list or a str")

        sql.append(";")
        sql = " ".join(sql)
        with DBConnect(**cfg) as db:
            db.select(sql)
            returnlist = []
            for i in db:
                obj = Order(i)
                returnlist.append(obj)

        return returnlist

    @classmethod
    def get_user_scenes(cls, user_id, params=[]):
        scene_list = []
        user_orders = Order.where("user_id = {0}".format(user_id))
        for order in user_orders:
            scenes = order.scenes(params)
            if scenes:
                for i in scenes:
                    scene_list.append(i)

        return scene_list

    @classmethod
    def generate_ee_order_id(cls, email_addr, eeorder):
        '''Generate an order id if the order came from Earth Explorer

        Keyword args:
        email -- Email address of the requestor
        eeorder -- The Earth Explorer order id

        Return:
        An order id string for the espa system for ee created orders
        str(email-eeorder)
        '''
        return '%s-%s' % (email_addr, eeorder)

    @staticmethod
    def get_default_product_options():
        '''Factory method to return default product selection options

        Return:
        Dictionary populated with default product options
        '''
        o = {}
        # standard product selection options
        o['include_source_data'] = False            # underlying raster
        o['include_source_metadata'] = False        # source metadata
        o['include_customized_source_data'] = False
        o['include_sr_toa'] = False           # LEDAPS top of atmosphere
        o['include_sr_thermal'] = False       # LEDAPS band 6
        o['include_sr'] = False               # LEDAPS surface reflectance
        o['include_dswe'] = False             # Dynamic Surface Water
        o['include_sr_browse'] = False        # surface reflectance browse
        o['include_sr_ndvi'] = False          # normalized difference veg
        o['include_sr_ndmi'] = False          # normalized difference moisture
        o['include_sr_nbr'] = False           # normalized burn ratio
        o['include_sr_nbr2'] = False          # normalized burn ratio 2
        o['include_sr_savi'] = False          # soil adjusted vegetation
        o['include_sr_msavi'] = False         # modified soil adjusted veg
        o['include_sr_evi'] = False           # enhanced vegetation
        o['include_lst'] = False              # land surface temperature
        o['include_solr_index'] = False       # solr search index record
        o['include_cfmask'] = False           # (deprecated)
        o['include_statistics'] = False       # should we do stats & plots?

        return o

    @staticmethod
    def get_default_projection_options():
        '''Factory method to return default reprojection options

        Return:
        Dictionary populated with default reprojection options
        '''
        o = {}
        o['reproject'] = False             # reproject all rasters (True/False)
        o['target_projection'] = None      # if 'reproject' which projection?
        o['central_meridian'] = None       #
        o['false_easting'] = None          #
        o['false_northing'] = None         #
        o['origin_lat'] = None             #
        o['std_parallel_1'] = None         #
        o['std_parallel_2'] = None         #
        o['datum'] = 'wgs84'
        o['longitude_pole'] = None         #
        o['latitude_true_scale'] = None

        #utm only options
        o['utm_zone'] = None               # 1 to 60
        o['utm_north_south'] = None        # north or south

        return o

    @staticmethod
    def get_default_subset_options():
        '''Factory method to return default subsetting/framing options

        Return:
        Dictionary populated with default subsettings/framing options
        '''
        o = {}
        o['image_extents'] = False       # modify image extent(subset or frame)
        o['image_extents_units'] = None  # what units are the coords in?
        o['minx'] = None                 #
        o['miny'] = None                 #
        o['maxx'] = None                 #
        o['maxy'] = None                 #
        return o

    @staticmethod
    def get_default_resize_options():
        '''Factory method to return default resizing options

        Return:
        Dictionary populated with default resizing options
        '''
        o = {}
        #Pixel resizing options
        o['resize'] = False            # resize output pixel size (True/False)
        o['pixel_size'] = None         # if resize, how big (30 to 1000 meters)
        o['pixel_size_units'] = None   # meters or dd.

        return o

    @staticmethod
    def get_default_resample_options():
        '''Factory method to returns default resampling options

        Return:
        Dictionary populated with default resampling options
        '''
        o = {}
        o['resample_method'] = 'near'  # how would user like to resample?

        return o

    @staticmethod
    def get_default_output_format():
        ''' Returns the default ESPA output format'''
        o = {}
        o['output_format'] = 'gtiff'
        return o

    @classmethod
    def get_default_options(cls):
        '''Factory method to return default espa order options

        Return:
        Dictionary populated with default espa ordering options
        '''
        o = {}
        o.update(cls.get_default_product_options())
        o.update(cls.get_default_projection_options())
        o.update(cls.get_default_subset_options())
        o.update(cls.get_default_resize_options())
        o.update(cls.get_default_resample_options())
        o.update(cls.get_default_output_format())

        return o

    @staticmethod
    def get_default_ee_options():
        '''Factory method to return default espa order options for orders
        originating in through Earth Explorer

        Return:
        Dictionary populated with default espa options for ee
        '''
        o = Order.get_default_options()
        o['include_sr'] = True

        return o

    def user_email(self):
        sql = "select email from auth_user where id = {0};".format(self.user_id)
        with DBConnect(**cfg) as db:
            db.select(sql)
            return db[0]['email']

    def save(self):
        sql_list = ["UPDATE ordering_order SET "]
        attr_tup = ('orderid', 'status', 'order_source', 'product_options', 'product_opts',
                    'order_type', 'initial_email_sent', 'completion_email_sent',
                    'note', 'completion_date', 'order_date', 'user_id', 'ee_order_id',
                    'email', 'priority')
        null_fields = ('ordering_date', 'completion_date', 'initial_email_sent',
                        'completion_email_sent', 'product_opts')
        for idx, attr in enumerate(attr_tup):
            val = self.__getattribute__(attr)
            if val is None:
                if attr in null_fields:
                    sql_snip = "{0} = {1}, "
                    val = 'null'
                else:
                    sql_snip = "{0} = '{1}', "
                    val = ''
            else:
                if attr == "user_id":
                    sql_snip = "{0} = {1}, "
                elif attr == "product_opts":
                    sql_snip = "{0} = {1},  "
                    # subsequent call to order.product_opts returns Json object
                    # only way could get the insert into the db. method for
                    # returning str from that is getquoted()
                    val = Json(self.product_opts)
                else:
                    sql_snip = "{0} = '{1}', "

            if idx == len(attr_tup) - 1:
                sql_snip = sql_snip.replace(",", "")

            sql_snip = sql_snip.format(attr, val)

            sql_list.append(sql_snip)

        sql_list.append("WHERE id = {0};".format(self.id))

        sql = " ".join(sql_list)
        logger.info("saving updates to order {0}\n sql: {1}\n\n".format(self.orderid, sql))
        #return sql

        with DBConnect(**cfg) as db:
            db.execute(sql)
            db.commit()
        return True

    def update(self, att, val):
        self.__setattr__(att, val)
        if isinstance(val, str) or isinstance(val, datetime.datetime):
            val = "\'{0}\'".format(val)
        sql = "update ordering_order set {0} = {1} where id = {2};".format(att, val, self.id)
        #return sql
        with DBConnect(**cfg) as db:
            db.execute(sql)
            db.commit()
        return True

    def scenes(self, conditions=[]):
        conditions.append("order_id = {0}".format(self.id))
        sql = " AND ".join(conditions)
        slist = Scene.where(sql)
        return slist

