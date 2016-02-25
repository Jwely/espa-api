from decimal import Decimal

import validictory
from validictory.validator import RequiredFieldValidationError, SchemaError, DependencyValidationError
import api.providers.ordering.ordering_provider as ordering


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

        # This assumes that the only two valid unit options is
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
