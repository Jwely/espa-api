""" Holds domain objects for orders and the items attached to them """
import json
import datetime
import copy

from api.util.dbconnect import DBConnectException, db_instance
from api.domain.scene import Scene
from api.domain import sensor
from api.system.logger import ilogger as logger
from psycopg2.extras import Json

class OrderException(Exception):
    pass

class Order(object):
    """ Class for interacting with the ordering_order table """

    base_sql = "SELECT id, orderid, email, order_date, status, product_options,"\
                "order_source, ee_order_id, user_id, order_type, priority,"\
                "completion_date, note, initial_email_sent,"\
                "completion_email_sent, product_opts FROM ordering_order WHERE "

    def __init__(self, orderid=None, status=None, order_source=None, order_type=None,
                product_options=None, product_opts=None, initial_email_sent=None,
                completion_email_sent=None, note=None, completion_date=None,
                order_date=None, user_id=None, ee_order_id=None, email=None,
                priority=None):
                self.orderid = orderid
                self.status = status
                self.order_source = order_source
                self.order_type = order_type
                self.product_options = product_options
                self.product_opts = product_opts
                self.initial_email_sent = initial_email_sent
                self.completion_email_sent = completion_email_sent
                self.note = note
                self.completion_date = completion_date
                self.order_date = order_date
                self.user_id = user_id
                self.ee_order_id = ee_order_id
                self.email = email
                self.priority = priority
                with db_instance() as db:
                    db.select("select id from ordering_order where orderid = '{0}';".format(orderid))
                    if db:
                        self.id = db[0]['id']
                    else:
                        self.id = None

    def __repr__(self):
        return "Order:{0}".format(self.__dict__)

    @classmethod
    def create(cls, params):
        """
        Place a new order into the system
        :param params: dict of required parameters to be used
            params = {'product_opts': {dictionary object of the order received}
                      'orderid': id generated from generate_order_id
                      'user_id': EE user id
                      'order_type': typically 'level2_ondemand'
                      'status': 'ordered'
                      'note': user notes
                      'ee_order_id': earth explorer order id, or '' not through EE
                      'order_source': 'espa' or 'ee'
                      'order_date': date time string
                      'priority': legacy item, should be 'normal'
                      'email': user's contact email
                      'product_options': legacy, transitioning from json to jsonb}
        :return: order object
        """
        opts = params['product_opts']
        params['product_opts'] = json.dumps(params['product_opts'])

        # needed for orders coming in from EE. Need to drop use
        #  of 'product_options' entirely
        if 'product_options' not in params.keys():
            params['product_options'] = ''

        sql = ("INSERT INTO ordering_order (orderid, user_id, order_type, status,"
               "note, product_opts, ee_order_id, order_source, order_date, "
               "priority, email, product_options)"
               " VALUES (%(orderid)s, %(user_id)s, %(order_type)s, %(status)s,"
               " %(note)s, %(product_opts)s, %(ee_order_id)s, %(order_source)s, "
               "%(order_date)s, %(priority)s, %(email)s, %(product_options)s)")

        logger.info("Order creation parameters: {0}".format(params))

        try:
            with db_instance() as db:
                logger.info('New order complete SQL: {}'.format(db.cursor.mogrify(sql, params)))
                db.execute(sql, params)
                db.commit()
        except DBConnectException, e:
            raise OrderException("error creating new order: {0}\n sql: {1}\n".format(e.message, sql))

        order = Order.where("orderid = '{0}'".format(params['orderid']))[0]

        # Let the load_ee_order method handle the scene injection
        # as there is special logic for interacting with LTA
        if params['ee_order_id']:
            return order

        sensor_keys = sensor.SensorCONST.instances.keys()

        bulk_ls = []
        for key in opts:
            if key in sensor_keys:
                sensor_type = ''
                item1 = opts[key]['inputs'][0]

                if isinstance(sensor.instance(item1), sensor.Landsat):
                    sensor_type = 'landsat'
                elif isinstance(sensor.instance(item1), sensor.Modis):
                    sensor_type = 'modis'

                for s in opts[key]['inputs']:
                    scene_dict = {'name': s,
                                  'sensor_type': sensor_type,
                                  'order_id': order.id,
                                  'status': 'submitted',
                                  'ee_unit_id': None}

                    bulk_ls.append(scene_dict)

        if 'plot_statistics' in opts and opts['plot_statistics']:
            scene_dict = {'name': 'plot',
                          'sensor_type': 'plot',
                          'order_id': order.id,
                          'status': 'ordered',
                          'ee_unit_id': None}

            bulk_ls.append(scene_dict)

        Scene.create(bulk_ls)

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
        results = []
        with db_instance() as db:
            db.select(sql)
            returnlist = []
            for i in db:
                results.append(i)

        returnlist = []
        for i in results:
            od = dict(i)
            del od["id"]
            order = Order(**od)
            returnlist.append(order)

        return returnlist

    @classmethod
    def get_user_scenes(cls, user_id, params=None):
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
    def get_default_ee_options(item_ls):
        """
        Factory method to return default ESPA order options for orders
        originating through Earth Explorer

        :param item_ls: list of scenes received from EE for an order
                        structure: list({sceneid:, unit_num:})
        :return: dictionary representation of the EE order
        """
        ee_order = {}
        ee_order['format'] = 'Gtiff'
        for item in item_ls:
            try:
                scene_info = sensor.instance(item['sceneid'])
            except Exception:
                log_msg = 'Received unsupported product via EE: {}'.format(item['sceneid'])
                logger.debug(log_msg)
                continue

            short = scene_info.shortname

            if short not in ee_order:
                if isinstance(scene_info, sensor.Landsat):
                    ee_order[short] = {'inputs': [],
                                       'products': ['sr']}
                elif isinstance(scene_info, sensor.Modis):
                    ee_order[short] = {'inputs': [],
                                       'products': ['l1']}

            ee_order[short]['inputs'].append(item['sceneid'])

        return ee_order

    def user_email(self):
        sql = "select email from auth_user where id = {0};".format(self.user_id)
        with db_instance() as db:
            db.select(sql)
            return db[0]['email']

    def save(self):
        attr_tup = ('orderid', 'status', 'order_source', 'product_options', 'product_opts',
                    'order_type', 'initial_email_sent', 'completion_email_sent',
                    'note', 'completion_date', 'order_date', 'user_id', 'ee_order_id',
                    'email', 'priority')
        null_fields = ('ordering_date', 'completion_date', 'initial_email_sent',
                        'completion_email_sent', 'product_opts')

        if self.id:
            # this is an existing order
            sql_list = ["UPDATE ordering_order SET "]
            snip_pre = "{0} = "
        else:
            # this is a new order
            sql_list = ["INSERT INTO ordering_order "]
            sql_list.append(" {0} VALUES (".format(attr_tup))
            snip_pre = "{0}"


        for idx, attr in enumerate(attr_tup):
            val = self.__getattribute__(attr)
            if val is None:
                if attr in null_fields:
                    sql_snip = "{1}, "
                    val = 'null'
                else:
                    sql_snip = "'{1}', "
                    val = ''
            else:
                if attr == "user_id":
                    sql_snip = "{1}, "
                elif attr == "product_opts":
                    sql_snip = "{1},  "
                    # subsequent call to order.product_opts returns Json object
                    # only way could get the insert into the db. method for
                    # returning str from that is getquoted()
                    val = Json(self.product_opts)
                else:
                    sql_snip = "'{1}', "

            if idx == len(attr_tup) - 1:
                sql_snip = sql_snip.replace(",", "")

            sql_snip = snip_pre + sql_snip

            if "=" in snip_pre:
                sql_snip = sql_snip.format(attr, val)
            else:
                sql_snip = sql_snip.format("", val)

            sql_list.append(sql_snip)

        if "=" in snip_pre:
            verbage = "saving updates to "
            sql_list.append("WHERE id = {0};".format(self.id))
        else:
            verbage = "creating "
            sql_list.append(");")

        sql = " ".join(sql_list)
        logger.info("{0} order {1}\n sql: {2}\n\n".format(verbage, self.orderid, sql))
        #return sql

        with db_instance() as db:
            db.execute(sql)
            db.commit()
        return True

    def update(self, att, val):
        self.__setattr__(att, val)
        if val is None:
            vale = "null"
        elif isinstance(val, str) or isinstance(val, datetime.datetime):
            val = "\'{0}\'".format(val)
        sql = "update ordering_order set {0} = {1} where id = {2};".format(att, val, self.id)
        #return sql
        with db_instance() as db:
            db.execute(sql)
            db.commit()
        return True

    def scenes(self, conditions=None):
        _conds = ["order_id = {0}".format(self.id)]
        if conditions:
          for i in conditions:
                _conds.append(i)

        sql = " AND ".join(_conds)
        slist = Scene.where(sql)
        return slist

    @staticmethod
    def generate_order_id(email):
        """
        Generate ESPA order id
        """
        d = datetime.datetime.now()

        return '{}-{}'.format(email, d.strftime('%m%d%Y-%H%M%S'))


class OptionsConversion(object):
    # [(old, new, old val)]
    aea_map = [('std_parallel_1', 'standard_parallel_1', None),
               ('std_parallel_2', 'standard_parallel_2', None),
               ('central_meridian', 'central_meridian', None),
               ('false_easting', 'false_easting', None),
               ('false_northing', 'false_northing', None),
               ('origin_lat', 'latitude_of_origin', None),
               ('datum', 'datum', None)]

    ps_map = [('longitude_pole', 'longitudinal_pole', None),
              ('latitude_true_scale', 'latitude_true_scale', None),
              ('false_easting', 'false_easting', None),
              ('false_northing', 'false_northing', None)]

    utm_map = [('utm_zone', 'zone', None),
               ('utm_north_south', 'zone_ns', None)]

    sinu_map = [('central_meridian', 'central_meridian', None),
                ('false_easting', 'false_easting', None),
                ('false_northing', 'false_northing', None)]

    lonlat_map = [(None, None, None)]

    proj_names_map = [('target_projection', 'aea', aea_map),
                      ('target_projection', 'ps', ps_map),
                      ('target_projection', 'utm', utm_map),
                      ('target_projection', 'lonlat', lonlat_map),
                      ('target_projection', 'sinu', sinu_map)]

    ext_map = [('image_extents_units', 'units', None),
               ('minx', 'west', None),
               ('miny', 'south', None),
               ('maxx', 'east', None),
               ('maxy', 'north', None)]

    res_map = [('pixel_size', 'pixel_size', None),
               ('pixel_size_units', 'pixel_size_units', None)]

    prod_map = [('include_source_data', 'l1', True),
                ('include_customized_source_data', 'l1', True),
                ('include_sourcefile', 'include_sourcefile', True),
                ('include_solr_index', 'include_solr_index', True),
                ('include_sca', 'include_sca', True),
                ('include_swe', 'include_swe', True),
                ('include_sr_browse', 'sr_browse', True),
                ('include_statistics', 'stats', True),
                ('include_source_metadata', 'source_metadata', True),
                ('include_sr_toa', 'toa', True),
                ('include_sr_thermal', 'bt', True),
                ('include_sr', 'sr', True),
                ('include_dswe', 'swe', True),
                ('include_sr_ndvi', 'sr_ndvi', True),
                ('include_sr_ndmi', 'sr_ndmi', True),
                ('include_sr_nbr', 'sr_nbr', True),
                ('include_sr_nbr2', 'sr_nbr2', True),
                ('include_sr_savi', 'sr_savi', True),
                ('include_sr_msavi', 'sr_msavi', True),
                ('include_sr_evi', 'sr_evi', True),
                ('include_lst', 'lst', True),
                ('include_cfmask', 'cloud', True)]

    keywords_map = [('resize', 'resize', res_map),
                    ('resample_method', 'resampling_method', None),
                    ('output_format', 'format', None),
                    ('image_extents', 'image_extents', ext_map),
                    ('reproject', 'projection', proj_names_map)]

    @classmethod
    def convert(cls, new=None, old=None, scenes=None):
        """
        Provides the conversion between old and new ordering
        options

        :param new: New formatted order options
        :param old: Old formatted order options
        :param scenes: List of scene id's associated with the order
        :return: converted format
        """
        exc_msg = ''
        if not new and not old:
            exc_msg = 'You must provide either new or old order options to convert'
        elif new and old:
            exc_msg = 'You must only provide either new or old options to convert, not both'
        elif old and not scenes:
            exc_msg = 'Scene list is required to properly convert to the new standard'

        if exc_msg:
            raise ValueError(exc_msg)

        if not new:
            new = {}
        if not old:
            old = {}
        if not scenes:
            scenes = []

        if not isinstance(new, dict):
            raise TypeError('Submitted options must be a dict')
        if not isinstance(old, dict):
            raise TypeError('Submitted options must be a dict')
        if not isinstance(scenes, (list, tuple)):
            raise TypeError('Submitted scenes must be list or tuple')

        if new:
            return cls._convert_new_to_old(new)
        elif old:
            return cls._convert_old_to_new(old, scenes)

    @classmethod
    def _convert_new_to_old(cls, opts):
        """
        Basically need to make a flat data structure
        and change the names used

        :param opts: order options in the new format
        :return: order options in the old format
        """
        ret = Order.get_default_options()

        ret.update(cls._flatten(opts, cls.keywords_map))

        return ret

    @classmethod
    def _convert_old_to_new(cls, old, scenes):
        """
        Have to turn a flat data structure into a nested one
        based on certain key names

        :param old: old product options format
        :param scenes: scenes associated with the order
        :return: nested dictionary
        """
        ret = {}
        opts = copy.deepcopy(old)

        old_prods, _, _ = zip(*cls.prod_map)

        prod_ls = []
        opts_keys = opts.keys()
        for key in opts_keys:
            if key in old_prods:
                if opts[key] is True:
                    prod_ls.append(key)
                opts.pop(key)  # Reduce further iterations

        prods = cls._translate(cls.prod_map, prod_ls).keys()

        if len(prods) < 1:
            prods.append('sr')

        if opts:
            ret.update(cls._build_nested(opts, cls.keywords_map))

        ret.update(cls._build_nested_sensors(prods, scenes))

        return ret

    @classmethod
    def _flatten(cls, opts, attr_map):
        ret = {}

        if opts is None:
            return ret

        sensor_keys = sensor.SensorCONST.instances.keys()

        old_attrs, new_attrs, conv_attrs = zip(*attr_map)
        # Reverse the old and new lists to reuse the _translate method
        conv_map = zip(new_attrs, old_attrs, conv_attrs)

        prod_ls = []
        for key, val in opts.items():
            if key in sensor_keys:
                prod_ls.extend(opts[key]['products'])

            elif key in new_attrs:
                idx = new_attrs.index(key)
                conv_attr = conv_attrs[idx]

                if isinstance(conv_attr, list):
                    ret.update(cls._translate(conv_map, {key: val}))
                    ret.update(cls._flatten(val, conv_attr))
                else:
                    ret.update(cls._translate(conv_map, {key: val}))

            elif key == 'plot_statistics':
                # No appropriate mapping as it is handled as a dummy scene in the DB
                continue

            else:
                raise ValueError('Unrecognized key: {}'.format(key))

        old_prods, new_prods, conv_prods = zip(*cls.prod_map)
        conv_map = zip(new_prods, old_prods, conv_prods)
        ret.update(cls._translate(conv_map, prod_ls))

        return ret

    @classmethod
    def _build_nested(cls, opts, attr_map):
        ret = {}

        old_attrs, new_attrs, conv_maps = zip(*attr_map)

        for key in opts:
            # Make sure we don't accidentally dismiss 0
            if key in old_attrs and (opts[key] is not False and
                                     opts[key] is not None):
                # Need to index based on the name for projections
                # so we only include the appropriate params
                if key == 'target_projection':
                    idx = new_attrs.index(opts[key])
                else:
                    idx = old_attrs.index(key)

                conv_map = conv_maps[idx]

                if isinstance(conv_map, list):
                    ret[new_attrs[idx]] = cls._build_nested(opts, conv_map)
                elif conv_map is None:
                    ret.update({new_attrs[idx]: opts[key]})
                else:
                    ret.update(cls._translate(conv_map, {key: opts[key]}))

        return ret

    @classmethod
    def _build_nested_sensors(cls, prods, scenes):
        ret = {}

        for scene in scenes:
            if scene == 'plot':
                ret.update({'plot_statistics': True})
                continue

            try:
                short = sensor.instance(scene).shortname
            except:  # Invalid scene identifier
                short = 'invalid'

            if short in ret:
                ret[short]['inputs'].append(scene)
            else:
                ret[short] = {'inputs': [scene],
                              'products': prods}

        return ret

    @classmethod
    def _translate(cls, transl_map, opts):
        ret = {}
        frm, to, conv = zip(*transl_map)

        o_major_keys, n_major_keys, _ = zip(*cls.keywords_map)

        for key in opts:
            try:
                idx = frm.index(key)
            except:
                exc_msg = '{} Not found in tuple: {}'.format(key, frm)
                raise ValueError(exc_msg)

            if isinstance(conv[idx], list):
                if key in n_major_keys:
                    ret.update({to[idx]: True})
                else:  # Catch projection names
                    ret.update({to[idx]: key})
            elif conv[idx] is not None:  # Predefined value
                ret.update({to[idx]: conv[idx]})
            else:  # Catch the value
                ret.update({to[idx]: opts[key]})

        return ret
