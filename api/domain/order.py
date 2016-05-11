""" Holds domain objects for orders and the items attached to them """
import json
import datetime
import copy

from api.util.dbconnect import DBConnectException, db_instance
import psycopg2.extensions as db_extns
from api.domain.scene import Scene
from api.domain import sensor
from api.system.logger import ilogger as logger
from psycopg2.extras import Json


class OrderException(Exception):
    pass


class Order(object):
    """ Class for interacting with the ordering_order table """

    base_sql = ('SELECT * '
                'FROM ordering_order '
                'WHERE ')

    def __init__(self, orderid=None, status=None, order_source=None,
                 order_type=None, product_options=None,
                 product_opts=None, initial_email_sent=None,
                 completion_email_sent=None, note=None,
                 completion_date=None, order_date=None, user_id=None,
                 ee_order_id=None, email=None, priority=None):
        """
        Initialize the Order object with all the information for it
        from the database

        All parameters are directly related to DB columns

        :param orderid: order ID long name, someone@someplace-123456
        :param status: current status in the system
        :param order_source: origination of the Order, earthexplorer or ESPA
        :param order_type: typically 'level2_ondemand'
        :param product_options: legacy column
        :param product_opts: dict representation of the order
        :param initial_email_sent: date
        :param completion_email_sent: date
        :param note: user note on the order
        :param completion_date: date
        :param order_date: date
        :param user_id: earth explorer ID of the user
        :param ee_order_id: ID used by EE to track the order
        :param email: user email
        :param priority: legacy
        """
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
            sql = 'select id from ordering_order where orderid = %s'
            db.select(sql, orderid)
            if db:
                self.id = db[0]['id']
            else:
                self.id = None

    def __repr__(self):
        return 'Order: {}'.format(self.__dict__)

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
                      'ee_order_id': earth explorer order id, or ''
                      'order_source': 'espa' or 'ee'
                      'order_date': date time string
                      'priority': legacy item, should be 'normal'
                      'email': user's contact email
                      'product_options': legacy column}
        :return: order object
        """
        opts = params['product_opts']

        params['product_opts'] = json.dumps(params['product_opts'])

        sql = ('INSERT INTO ordering_order '
               '(orderid, user_id, order_type, status, note, '
               'product_opts, ee_order_id, order_source, order_date, '
               'priority, email, product_options) '
               'VALUES (%(orderid)s, %(user_id)s, %(order_type)s, '
               '%(status)s, %(note)s, %(product_opts)s, '
               '%(ee_order_id)s, %(order_source)s, %(order_date)s, '
               '%(priority)s, %(email)s, %(product_options)s)')

        logger.info('Order creation parameters: {}'.format(params))

        log_sql = ''
        try:
            with db_instance() as db:
                log_sql = db.cursor.mogrify(sql, params)
                logger.info('New order complete SQL: {}'
                            .format(log_sql))
                db.execute(sql, params)
                db.commit()
        except DBConnectException as e:
            logger.debug('Error creating new order: {}\n'
                         'sql: {}'.format(e.message, log_sql))
            raise OrderException(e)

        order = Order.where({'orderid': params['orderid']})[0]

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
                          'status': 'submitted',
                          'ee_unit_id': None}

            bulk_ls.append(scene_dict)

        Scene.create(bulk_ls)

        return order

    @classmethod
    def where(cls, params, sql_and=None):
        """
        Query for a particular row in the ordering_oder table

        :param params: dictionary of column: value parameter to select on
        :param sql_and: custom query parameter for anything besides =
        :return: list of matching Order objects
        """
        if not isinstance(params, dict):
            raise OrderException('Where arguments must be '
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
                logger.info('order.py where sql: {}'.format(log_sql))

                db.select(sql, (db_extns.AsIs(fields), values))

                for i in db:
                    od = dict(i)
                    del od['id']
                    obj = Order(**od)
                    ret.append(obj)
        except DBConnectException as e:
            logger.debug('Error order where: {}\n'
                         'sql: {}'.format(e.message, log_sql))
            raise OrderException(e)

        if not ret:
            logger.warning('Error where returned no results\n'
                           'sql: {}'.format(log_sql))

        return ret

    @classmethod
    def get_user_scenes(cls, user_id, params=None):
        """
        Retrieve a list of scenes associated with a user

        :param user_id: user info
        :param params: additional SQL query parameters
        :return: list of scene objects
        """
        scene_list = []
        user_orders = Order.where({'user_id': user_id})
        for order in user_orders:
            scenes = order.scenes(sql_and=params)
            if scenes:
                for i in scenes:
                    scene_list.append(i)

        return scene_list

    @classmethod
    def generate_ee_order_id(cls, email_addr, eeorder):
        """
        Generate an order id if the order came from Earth Explorer

        :param eeorder: The Earth Explorer order id
        :param email_addr: Email address of the requestor
        :return: An order id string for the ESPA system for ee created orders
        """
        return '{}-{}'.format(email_addr, eeorder)

    @staticmethod
    def get_default_product_options():
        """
        LEGACY METHOD

        Factory method to return default product selection options

        :return: Dictionary populated with default product options
        """
        # standard product selection options
        o = {'include_source_data': False,  # underlying raster
             'include_source_metadata': False,  # source metadata
             'include_customized_source_data': False,
             'include_sr_toa': False,  # LEDAPS top of atmosphere
             'include_sr_thermal': False,  # LEDAPS band 6
             'include_sr': False,  # LEDAPS surface reflectance
             'include_dswe': False,  # Dynamic Surface Water
             'include_sr_browse': False,  # surface reflectance browse
             'include_sr_ndvi': False,  # normalized difference veg
             'include_sr_ndmi': False,  # normalized difference moisture
             'include_sr_nbr': False,  # normalized burn ratio
             'include_sr_nbr2': False,  # normalized burn ratio 2
             'include_sr_savi': False,  # soil adjusted vegetation
             'include_sr_msavi': False,  # modified soil adjusted veg
             'include_sr_evi': False,  # enhanced vegetation
             'include_lst': False,  # land surface temperature
             'include_solr_index': False,  # solr search index record
             'include_cfmask': False,  # (deprecated) not
             'include_statistics': False}  # should we do stats & plots?

        return o

    @staticmethod
    def get_default_projection_options():
        """
        LEGACY METHOD

        Factory method to return default reprojection options

        :return: Dictionary populated with default reprojection options
        """
        o = {'reproject': False,
             'target_projection': None,
             'central_meridian': None,
             'false_easting': None,
             'false_northing': None,
             'origin_lat': None,
             'std_parallel_1': None,
             'std_parallel_2': None,
             'datum': 'wgs84',
             'longitude_pole': None,
             'latitude_true_scale': None,
             'utm_zone': None,
             'utm_north_south': None}

        return o

    @staticmethod
    def get_default_subset_options():
        """
        LEGACY METHOD

        Factory method to return default subsetting/framing options

        :return: Dictionary populated with default subsettings/framing
         options
        """
        o = {'image_extents': False,
             'image_extents_units': None,
             'minx': None,
             'miny': None,
             'maxx': None,
             'maxy': None}

        return o

    @staticmethod
    def get_default_resize_options():
        """
        LEGACY METHOD

        Factory method to return default resizing options

        :return: Dictionary populated with default resizing options
        """
        o = {'resize': False,
             'pixel_size': None,
             'pixel_size_units': None}

        return o

    @staticmethod
    def get_default_resample_options():
        """
        LEGACY METHOD

        Factory method to returns default resampling options

        :return: Dictionary populated with default resampling options
        """
        o = {'resample_method': 'near'}

        return o

    @staticmethod
    def get_default_output_format():
        """
        LEGACY METHOD

        :return: Returns the default ESPA output format
        """
        o = {'output_format': 'gtiff'}

        return o

    @classmethod
    def get_default_options(cls):
        """
        LEGACY METHOD

        Factory method to return default espa order options

        :return: Dictionary populated with default espa ordering options
        """
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
        ee_order = {'format': 'gtiff'}
        for item in item_ls:
            try:
                scene_info = sensor.instance(item['sceneid'])
            except sensor.ProductNotImplemented:
                log_msg = ('Received unsupported product via EE: {}'
                           .format(item['sceneid']))
                logger.debug(log_msg)
                continue

            short = scene_info.shortname

            if short in ee_order:
                ee_order[short]['inputs'].append(item['sceneid'])
            else:
                if isinstance(scene_info, sensor.Landsat):
                    ee_order[short] = {'inputs': [item['sceneid']],
                                       'products': ['sr']}
                elif isinstance(scene_info, sensor.Modis):
                    ee_order[short] = {'inputs': [item['sceneid']],
                                       'products': ['l1']}

        return ee_order

    def user_email(self):
        """
        Retrieve the email address associated with this order

        :return: email address
        """
        sql = 'select email from auth_user where id = %s'

        ret = None
        log_sql = ''
        try:
            with db_instance() as db:
                log_sql = db.cursor.mogrify(sql, (self.user_id,))
                logger.info('order.py user_email: {}'.format(log_sql))

                db.select(sql, self.user_id)

                ret = db[0]['email']
        except DBConnectException as e:
            logger.debug('Error retrieving user_email: {}'
                         .format(log_sql))
            raise OrderException(e)

        return ret

    def save(self):
        """
        Upsert self to the database
        """
        sql = ('INSERT INTO ordering_order %s VALUES %s '
               'ON CONFLICT (orderid) '
               'DO UPDATE '
               'SET %s = %s')

        attr_tup = ('orderid', 'status', 'order_source',
                    'product_options', 'product_opts', 'order_type',
                    'initial_email_sent', 'completion_email_sent',
                    'note', 'completion_date', 'order_date', 'user_id',
                    'ee_order_id', 'email', 'priority')

        vals = tuple(self.__getattribute__(v)
                     if v != 'product_opts'
                     else json.dumps(self.__getattribute__(v))
                     for v in attr_tup)

        cols = '({})'.format(','.join(attr_tup))

        log_sql = ''
        try:
            with db_instance() as db:
                log_sql = db.cursor.mogrify(sql, (db_extns.AsIs(cols),
                                                  vals,
                                                  db_extns.AsIs(cols),
                                                  vals))
                db.execute(sql, (db_extns.AsIs(cols), vals,
                                 db_extns.AsIs(cols), vals))
                db.commit()

                logger.info('Saved updates to order id: {}\n'
                            'order.id: {}\nsql: {}\nargs: {}'
                            .format(self.orderid, self.id, log_sql,
                                    zip(attr_tup, vals)))
        except DBConnectException as e:
            logger.debug('Error saving order: {}\nsql: {}'
                         .format(e.message, log_sql))

            raise OrderException(e)

        new = Order.where({'id': self.id})[0]

        for att in attr_tup:
            self.__setattr__(att, new.__getattribute__(att))

    def update(self, att, val):
        """
        Update a specified column value for this Order object

        :param att: column to update
        :param val: new value
        :return: updated value from self
        """
        sql = 'update ordering_order set %s = %s where id = %s'

        log_sql = ''
        try:
            with db_instance() as db:
                log_sql = db.cursor.mogrify(sql, (db_extns.AsIs(att),
                                                  val, self.id))
                logger.info(log_sql)
                db.execute(sql, (db_extns.AsIs(att), val, self.id))
                db.commit()
        except DBConnectException as e:
            logger.debug('Error updating order: {}\nSQL: {}'
                         .format(e.message, log_sql))

        self.__setattr__(att, val)

        return self.__getattribute__(att)

    def scenes(self, sql_dict=None, sql_and=None):
        """
        Retrieve a list of Scene objects related to this
        initialized Order object

        :param sql_dict: dictionary object for sql parameters
        :param sql_and: additional query parameters
        :return: list of Scene objects
        """
        if sql_dict:
            sql_dict['order_id'] = self.id
        else:
            sql_dict = {'order_id': self.id}

        return Scene.where(sql_dict, sql_and=sql_and)

    def products_by_sensor(self):
        """
        Return a dictionary of the requested products, keyed on sensor

        :return: dictionary of products
        """
        po = self.product_opts
        _out_list = []
        prod_out = {}
        for k, v in po.iteritems():
            if isinstance(po[k], dict) and 'products' in po[k].keys():
                _out_list.append(po[k])

        for item in _out_list:
            for input in item['inputs']:
                prod_out[input] = item['products']

        return prod_out

    @staticmethod
    def generate_order_id(email):
        """
        Generate ESPA order id

        :param email: email associated with the order
        :return: longname for an order_id, someone@someplace-1234556
        """
        d = datetime.datetime.now()

        return '{}-{}'.format(email, d.strftime('%m%d%Y-%H%M%S'))


class OptionsConversion(object):
    """
    Provides a means to convert between the old legacy product_options
    format to the new JSON/dict product_opts format
    """

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

    resize_map = [('pixel_size', 'pixel_size', None),
                  ('pixel_size_units', 'pixel_size_units', None)]

    prod_map = [('include_customized_source_data', 'l1', True),
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

    resample_map = [('cubic', 'cc', None),
                    ('near', 'nn', None),
                    ('bilinear', 'bil', None)]

    keywords_map = [('resize', 'resize', resize_map),
                    ('resample_method', 'resampling_method', resample_map),
                    ('output_format', 'format', None),
                    ('image_extents', 'image_extents', ext_map),
                    ('reproject', 'projection', proj_names_map)]

    # Key words in which can have nested properties
    majorwords = [('resize', 'resize'),
                  ('image_extents', 'image_extents'),
                  ('reproject', 'projection')]

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
        exc_msg = None
        if not new and not old:
            exc_msg = 'You must provide either new or old order options to convert'
        elif new and old:
            exc_msg = 'You must only provide either new or old options to convert, not both'
        elif not scenes:
            exc_msg = 'Scenes are required to properly convert between the standards'

        if exc_msg:
            raise ValueError(exc_msg)

        if not new:
            new = {}
        if not old:
            old = {}

        if not isinstance(new, dict):
            raise TypeError('Submitted options must be a dict')
        if not isinstance(old, dict):
            raise TypeError('Submitted options must be a dict')
        if not isinstance(scenes, (list, tuple)):
            raise TypeError('Submitted scene(s) must be list or tuple')

        if new:
            return cls._convert_new_to_old(new, scenes[0])
        elif old:
            return cls._convert_old_to_new(old, scenes)

    @classmethod
    def _convert_new_to_old(cls, opts, scene):
        """
        Basically need to make a flat data structure
        and change the names used

        :param opts: order options in the new format
        :return: order options in the old format
        """
        ret = Order.get_default_options()
        opts = copy.deepcopy(opts)

        short = sensor.instance(scene).shortname
        sen_keys = sensor.SensorCONST.instances.keys()

        for sen in sen_keys:
            if sen in opts and sen != short:
                opts.pop(sen)

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
        """
        Attempt to bring nested objects to the same level

        :param opts: nested struct to work on
        :param attr_map: conversion mapping
        :return: flat dictionary
        """
        ret = {}

        if opts is None or not isinstance(opts, dict):
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
                # No appropriate mapping as it is handled as a dummy
                # scene in the DB
                continue
            elif key == 'note':
                continue
            else:
                raise ValueError('Unrecognized key: {}'.format(key))

        old_prods, new_prods, conv_prods = zip(*cls.prod_map)
        conv_map = zip(new_prods, old_prods, conv_prods)
        ret.update(cls._translate(conv_map, prod_ls))

        return ret

    @classmethod
    def _build_nested(cls, opts, attr_map):
        """
        Attempt to build a nested data structure based on attribute
        mappings

        :param opts: attributes to nest
        :param attr_map: conversion mapping
        :return: nested dictionary structure
        """
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
                    ret[new_attrs[idx]] = cls._build_nested(opts,
                                                            conv_map)
                elif conv_map is None:
                    ret.update({new_attrs[idx]: opts[key]})
                else:
                    ret.update(cls._translate(conv_map,
                                              {key: opts[key]}))

        return ret

    @classmethod
    def _build_nested_sensors(cls, prods, scenes):
        """
        Build the nested sensor structures

        :param prods: associated products
        :param scenes: associated scenes
        :return: nested sensor structures
        """
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
        """
        Convert the specified options

        :param transl_map: conversion map to use
        :param opts: options to convert
        :return: converted namings
        """
        ret = {}
        frm, to, conv = zip(*transl_map)

        o_major_keys, n_major_keys = zip(*cls.majorwords)

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
                    if key == 'resampling_method':
                        continue
                    ret.update({to[idx]: key})
            elif conv[idx] is not None:  # Predefined value
                ret.update({to[idx]: conv[idx]})
            else:  # Catch the value
                ret.update({to[idx]: opts[key]})

        return ret
