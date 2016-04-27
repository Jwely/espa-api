from __future__ import absolute_import
from decimal import Decimal
import copy

import validictory
from validictory.validator import RequiredFieldValidationError, SchemaError, DependencyValidationError

from api.providers.validation import ValidationInterfaceV0
from api import ValidationException
import api.providers.ordering.ordering_provider as ordering
import api.domain.sensor as sn


class OrderValidatorV0(validictory.SchemaValidator):
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username')
        super(OrderValidatorV0, self).__init__(*args, **kwargs)
        self.data_source = None
        self.base_schema = None
        self._itemcount = None

    def validate(self, data, schema):
        self.data_source = data
        self.base_schema = schema
        self._itemcount = {}
        super(OrderValidatorV0, self).validate(data, schema)

    def validate_extents(self, x, fieldname, schema, path, pixel_count=200000000):
        params = x.get(fieldname)
        required_params = ['north', 'south', 'east', 'west', 'units']

        calc_args = {'xmax': None,
                     'ymax': None,
                     'xmin': None,
                     'ymin': None,
                     'ext_units': None,
                     'res_units': None,
                     'res_pixel': None}

        # Since we can't predict which validation methods are called first
        # we need to make sure that all the values are present and are of
        # the correct type, let the other built-in validations handle the actual
        # error output for most failures
        if self.validate_type_object(params):
            if not set(params.keys()).symmetric_difference(set(required_params)):
                if 'projection' not in x or not x['projection']:
                    return
                if not self.validate_type_number(params['east']):
                    return
                if not self.validate_type_number(params['north']):
                    return
                if not self.validate_type_number(params['west']):
                    return
                if not self.validate_type_number(params['south']):
                    return
                if not self.validate_type_string(params['units']):
                    return
                if not params['units'] in schema['properties']['units']['enum']:
                    return
                if 'lonlat' in x['projection'] and params['units'] != 'dd':
                    self._error('must be "dd" for projection "lonlat"', params['units'], fieldname, path=path)
                    return

                if 'resize' in x and 'pixel_resize_units' in x['resize'] and 'pixel_size' in x['resize']:
                    if self.validate_type_string(x['resize']['pixel_resize_units']):
                        if self.validate_type_number(x['resize']['pixel_size']):
                            if x['resize']['pixel_size'] <= 0:
                                return
                            else:
                                calc_args['res_pixel'] = x['resize']['pixel_size']
                                calc_args['res_units'] = x['resize']['pixel_resize_units']

                calc_args['xmax'] = params['east']
                calc_args['ymax'] = params['north']
                calc_args['xmin'] = params['west']
                calc_args['ymin'] = params['south']
                calc_args['ext_units'] = params['units']

                count = self.calc_extent(**calc_args)
                if count > pixel_count:
                    self._error(': pixel count value is greater than maximum size of {} pixels'.format(pixel_count),
                                count, fieldname, path=path)
                elif count < 1:
                    self._error(': pixel count value falls below acceptable threshold, check extent parameters',
                                count, fieldname, path=path)

    @staticmethod
    def calc_extent(xmax, ymax, xmin, ymin, ext_units, res_units=None, res_pixel=None):
        """Calculate a good estimate of the number of pixels contained in an extent"""
        xdif = 0
        ydif = 0

        if ext_units == 'dd' and xmin > 170 and -170 > xmax:
            xdif = 360 - xmin + xmax
        elif xmax > xmin:
            xdif = xmax - xmin

        if ymax > ymin:
            ydif = ymax - ymin

        # Default values are actually sensor dependant and
        # should come from sensor.py, but this should be
        # sufficient for this purpose
        if not res_units:
            res_units = ext_units
            if ext_units == 'dd':
                res_pixel = 0.0002695
            else:
                res_pixel = 30

        # This assumes that the only two valid unit options are
        # decimal degrees and meters
        if res_units != ext_units:
            if ext_units == 'dd':
                res_pixel /= 111317.254174397
            else:
                res_pixel *= 111317.254174397

        return int(xdif * ydif / res_pixel ** 2)

    def validate_single_obj(self, x, fieldname, schema, path, single=False):
        """Validates that only one dictionary object was passed in"""
        value = x.get(fieldname)

        if isinstance(value, dict):
            if single:
                if len(value) > 1:
                    self._error(': field only accepts one object',
                                len(value), fieldname, path=path)

    def validate_enum_keys(self, x, fieldname, schema, path, valid_list):
        """Validates the keys in the given object match expected keys"""
        value = x.get(fieldname)

        if value is not None:

            if not hasattr(value, '__iter__'):
                value = [value]

            for field in value:
                if field not in valid_list:
                    self._error('Unknown key: Allowed keys {}'.format(valid_list),
                                field, fieldname, path=path)

    def validate_abs_rng(self, x, fieldname, schema, path, val_range):
        """Validates that the absolute value of a field falls within a given range"""
        value = x.get(fieldname)

        if isinstance(value, (int, long, float, Decimal)):
            if not val_range[0] < abs(value) < val_range[1]:
                self._error('Absolute value must fall between {} and {}'.format(val_range[0], val_range[1]),
                            value, fieldname, path=path)

    def validate_ps_dd_rng(self, x, fieldname, schema, path, val_range):
        """Validates the pixel size given for Decimal Degrees is within a given range"""
        value = x.get(fieldname)

        if isinstance(value, (int, long, float, Decimal)):
            if 'pixel_size_units' in x:
                if x['pixel_size_units'] == 'dd':
                    if not val_range[0] <= value <= val_range[1]:
                        self._error('Value must fall between {} and {}'.format(val_range[0], val_range[1]),
                                    value, fieldname, path=path)

    def validate_ps_meter_rng(self, x, fieldname, schema, path, val_range):
        """Validates the pixel size given for Meters is within a given range"""
        value = x.get(fieldname)

        if isinstance(value, (int, long, float, Decimal)):
            if 'pixel_size_units' in x:
                if x['pixel_size_units'] == 'meters':
                    if not val_range[0] <= value <= val_range[1]:
                        self._error('Value must fall between {} and {}'.format(val_range[0], val_range[1]),
                                    value, fieldname, path=path)

    def validate_role_restricted(self, x, fieldname, schema, path, restricted):
        if not restricted:
            return

        # Like extents, we need to do some initial validation of the input up front,
        # and let those individual validators output the errors
        if 'inputs' not in x:
            return
        if not self.validate_type_array(x['inputs']):
            return

        req_prods = x.get(fieldname)

        if not req_prods:
            return

        acq = x['inputs'][0]
        avail_prods = ordering.OrderingProvider().available_products(acq, self.username)

        if 'not_implemented' in avail_prods:
            return

        for key in avail_prods:
            avail_prods = avail_prods[key]['outputs']

        dif = set(req_prods) - set(avail_prods)
        if dif:
            self._error('The requested product(s) is not available at this time', list(dif),
                        fieldname, path=path)

    def validate_oneormoreobjects(self, x, fieldname, schema, path, key_list):
        """Validates that at least one value is present from the list"""
        val = x.get(fieldname)

        if self.validate_type_object(val):
            for key in key_list:
                if key in val:
                    return

            self._error('No requests for products were submitted', None, None, path=path,
                        exctype=RequiredFieldValidationError)

    def validate_set_ItemCount(self, x, fieldname, schema, path, (key, val)):
        """Sets item count limits for multiple arrays across a potential order"""
        if key in self._itemcount:
            raise SchemaError('ItemCount {} set multiple times'.format(key))
        if not self.validate_type_integer(val):
            raise SchemaError('Max value for {} must be an integer'.format(key))

        self._itemcount[key] = {'count': 0, 'max': val}

    def validate_ItemCount(self, x, fieldname, schema, path, key):
        """
        Increment the count for the specified key

        Make sure the total count for the category does not exceed a max value
        """
        vals = x.get(fieldname)

        if not self.validate_type_array(vals):
            return

        self._itemcount[key]['count'] += len(vals)

        if self._itemcount[key]['count'] > self._itemcount[key]['max']:
            self._error('Count exceeds size limit of {max} for {key}', None, None,
                        exctype=DependencyValidationError, max=self._itemcount[key]['max'], key=key)


class BaseValidationSchema(object):
    formats = ['gtiff', 'hdf-eos2', 'envi']

    resampling_methods = ['nn', 'bil', 'cc']

    projections = {'aea': {'type': 'object',
                           'properties': {'standard_parallel_1': {'type': 'number',
                                                                  'required': True,
                                                                  'minimum': -90,
                                                                  'maximum': 90},
                                          'standard_parallel_2': {'type': 'number',
                                                                  'required': True,
                                                                  'minimum': -90,
                                                                  'maximum': 90},
                                          'central_meridian': {'type': 'number',
                                                               'required': True,
                                                               'minimum': -180,
                                                               'maximum': 180},
                                          'latitude_of_origin': {'type': 'number',
                                                                 'required': True,
                                                                 'minimum': -90,
                                                                 'maximum': 90},
                                          'false_easting': {'type': 'number',
                                                            'required': True},
                                          'false_northing': {'type': 'number',
                                                             'required': True},
                                          'datum': {'type': 'string',
                                                    'required': True,
                                                    'enum': ['wgs84', 'nad27', 'nad83']}}},
                   'utm': {'type': 'object',
                           'properties': {'zone': {'type': 'integer',
                                                   'required': True,
                                                   'minimum': 1,
                                                   'maximum': 60},
                                          'zone_ns': {'type': 'string',
                                                      'required': True,
                                                      'enum': ['north', 'south']}}},
                   'lonlat': {'type': 'null'},
                   'sinu': {'type': 'object',
                            'properties': {'central_meridian': {'type': 'number',
                                                                'required': True,
                                                                'minimum': -180,
                                                                'maximum': 180},
                                           'false_easting': {'type': 'number',
                                                             'required': True},
                                           'false_northing': {'type': 'number',
                                                              'required': True}}},
                   'ps': {'type': 'object',
                          'properties': {'longitudinal_pole': {'type': 'number',
                                                               'required': True,
                                                               'minimum': -180,
                                                               'maximum': 180},
                                         'latitude_true_scale': {'type': 'number',
                                                                 'required': True,
                                                                 'abs_rng': (60, 90)},
                                         'false_easting': {'type': 'number',
                                                             'required': True},
                                         'false_northing': {'type': 'number',
                                                            'required': True}}}}

    extents = {'north': {'type': 'number',
                         'required': True},
               'south': {'type': 'number',
                         'required': True},
               'east': {'type': 'number',
                        'required': True},
               'west': {'type': 'number',
                        'required': True},
               'units': {'type': 'string',
                         'required': True,
                         'enum': ['dd', 'meters']}}

    resize = {'pixel_size': {'type': 'number',
                             'required': True,
                             'ps_dd_rng': (0.0002695, 0.0449155),
                             'ps_meter_rng': (30, 5000)},
              'pixel_size_units': {'type': 'string',
                                   'required': True,
                                   'enum': ['dd', 'meters']}}

    request_schema = {'type': 'object',
                      'set_ItemCount': ('inputs', 5000),
                      'properties': {'projection': {'properties': projections,
                                                    'type': 'object',
                                                    # 'enum_keys': self.projections.keys(),
                                                    'single_obj': True},
                                     'image_extents': {'extents': 200000000,
                                                       'type': 'object',
                                                       'properties': extents,
                                                       # 'enum_keys': self.extents.keys(),
                                                       'dependencies': ['projection']},
                                     'format': {'type': 'string',
                                                'required': True,
                                                'enum': formats},
                                     'resize': {'type': 'object',
                                                'properties': resize},
                                     'resampling_method': {'type': 'string',
                                                           'enum': resampling_methods},
                                     'plot_statistics': {'type': 'boolean'},
                                     'note': {'type': 'string',
                                              'required': False,
                                              'blank': True}}}

    _sensor_reg = sn.SensorCONST.instances
    sensor_schema = {}
    for key in _sensor_reg:
        sensor_schema[key] = {'type': 'object',
                              'properties': {'inputs': {'type': 'array',
                                                        'required': True,
                                                        'ItemCount': 'inputs',
                                                        'uniqueItems': True,
                                                        'items': {'type': 'string',
                                                                  'pattern': _sensor_reg[key][0]}},
                                             'products': {'type': 'array',
                                                          'uniqueItems': True,
                                                          'required': True,
                                                          'role_restricted': True,
                                                          'items': {'type': 'string',
                                                                    'enum': sn.instance(
                                                                            _sensor_reg[key][2]).products}}}}

    request_schema['properties'].update(sensor_schema)
    request_schema['oneormoreobjects'] = sensor_schema.keys()

    valid_params = {'formats': {'formats': formats},
                    'resampling_methods': {'resampling_methods': resampling_methods},
                    'projections': projections}


class ValidationProvider(ValidationInterfaceV0):
    schema = BaseValidationSchema

    def validate(self, order, username):
        """
        Validate an incoming order to make sure everything is kosher

        :param order: incoming order dict
        :param username: username associated with the order
        :return: validated order
        """
        order = copy.deepcopy(order)
        try:
            v = OrderValidatorV0(format_validators=None, required_by_default=False, blank_by_default=False,
                                 disallow_unknown_properties=True, apply_default_to_data=False,
                                 fail_fast=False, remove_unknown_properties=False, username=username)

            v.validate(order, self.schema.request_schema)
            # validictory.validate(order, self.schema.request_schema, fail_fast=False, disallow_unknown_properties=True,
            #                      validator_cls=OrderValidatorV0, required_by_default=False)
        except validictory.MultipleValidationError as e:
            raise ValidationException(e.message)
        except validictory.SchemaError as e:
            raise ValidationException(e.message)

        return self.massage_formatting(order)

    @staticmethod
    def massage_formatting(order):
        """
        To avoid complications down the line, we need to ensure proper case formatting
        on the order, while still being somewhat case agnostic

        We also need to add 'stats' product to all the sensors if 'plot_statistics'
        was set to True

        :param order: incoming order after validation
        :return: order with the inputs reformatted
        """
        prod_keys = sn.SensorCONST.instances.keys()

        stats = False
        if 'plot_statistics' in order and order['plot_statistics']:
            stats = True

        for key in order:
            if key in prod_keys:
                item1 = order[key]['inputs'][0]

                prod = sn.instance(item1)

                if isinstance(prod, sn.Landsat):
                    order[key]['inputs'] = [s.upper() for s in order[key]['inputs']]
                elif isinstance(prod, sn.Modis):
                    order[key]['inputs'] = ('.'.join([p[0].upper(),
                                                      p[1].upper(),
                                                      p[2].lower(),
                                                      p[3],
                                                      p[4]]) for p in [s.split('.') for s in order[key]['inputs']])

                if stats:
                    if 'stats' not in order[key]['products']:
                        order[key]['products'].append('stats')

        return order

    def fetch_projections(self):
        """
        Pass along projection information
        :return: dict
        """
        return copy.deepcopy(self.schema.valid_params['projections'])

    def fetch_formats(self):
        """
        Pass along valid file formats
        :return: dict
        """
        return copy.deepcopy(self.schema.valid_params['formats'])

    def fetch_resampling(self):
        """
        Pass along valid resampling options
        :return: dict
        """
        return copy.deepcopy(self.schema.valid_params['resampling_methods'])

    def fetch_order_schema(self):
        """
        Pass along the schema used for validation
        :return: dict
        """
        return copy.deepcopy(self.schema.request_schema)

    __call__ = validate
