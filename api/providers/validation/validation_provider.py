from decimal import Decimal

import validictory


class ESPAOrderValidatorV0(validictory.SchemaValidator):
    def __init__(self, *args, **kwargs):
        super(ESPAOrderValidatorV0, self).__init__(*args, **kwargs)
        self.data_source = None

    def validate(self, data, schema):
        self.data_source = data
        super(ESPAOrderValidatorV0, self).validate(data, schema)

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

    def validate_oneormore(self, x, fieldname, schema, path, key_list):
        """Validates that at least one value is present from the list"""
        pass
        # if isinstance(x, dict):
        #     if isinstance(x[fieldname], dict):
        #         keys = x.get(fieldname).keys()
        #
        #         valid = False
        #         for key in keys:
        #             if key in key_list:
        #                 valid = True
        #
        #         if not valid:
        #             self._error()
