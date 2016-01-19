# TODO Look at maybe making the actual validation logic more generic and create a translation class
# TODO that pulls the appropriate data out of the schema/order to populate the required fields for
# TODO validation, this would better support future schema changes

import cerberus
from api.domain.sensor import instance, available_products, ProductNotImplemented


class ValidationException(Exception):
    pass


class ValidationProvider(object):
    """
    Validation class for incoming orders
    """
    def __init__(self, schema_cls, size_thresh=2000000, *args, **kwargs):
        self.validator = cerberus.Validator(schema_cls.request_schema)

        self.schema_cls = schema_cls
        self.schema = schema_cls.request_schema
        self.valid_params = schema_cls.valid_params

        self.size_thresh = size_thresh

        self.order = None
        self.errors = {}

    def _clear_errors(self):
        self.errors = {}

    def _add_error(self, name, err_msg):
        self.errors[name] = err_msg

    def validate(self, order):
        self._clear_errors()
        self.order = order

        self._validate_orderstruct()
        self._validate_scene_list()

        # For my sanity right now
        print self.errors

        if not self.errors:
            return True
        else:
            return False

    def __call__(self, *args, **kwargs):
        return self.validate(*args, **kwargs)

    def _validate_orderstruct(self):
        """
        Validate the incoming order structure against the schema
        the class was initialized with

        This will also validate most of the valid ranges on the
        numeric type entries

        Uses the cerberus module to perform the actual validation
        and writes any cerberus errors to the class errors dict
        """
        self.validator(self.order)

        if self.validator.errors:
            self._add_error('Schema Error', self.validator.errors)

    def _validate_scene_list(self):
        """
        Validate the scene list and requested sensors with the available products

        Uses the sensor.py module to gather the available processing products for the
        given sensors

        Writes any errors to the class errors dict
        """
        errors = {}

        results = available_products(self.order['inputs'])

        if 'not_implemented' in results:
            errors['Sensor ID Not Recognized'] = results['not_implemented']
            results.pop('not_implemented', None)

        supported_prods = []
        for sensor in results:
            supported_prods.extend(results[sensor]['outputs'])

        unsupported = list(set(self.order['products']) - set(supported_prods))

        if unsupported:
            errors['Unsupported Product'] = unsupported

        if errors:
            self._add_error('Requested Products Error', errors)

    def _validate_projection_units(self):
        """
        Check to make sure that requested extent units make sense
        with the projection units

        The main purpose is to make sure someone doesn't submit
        extents given in meters for a geographic projection
        """
        pass

    def _validate_image_extents(self):
        """
        Verifies that the requested image extents are valid

        Coordinates given should make sense based on unit type
        maxx > minx
        maxy > miny

        Total number of pixels do not exceed a processing threshold
        """
        errors = {}

        maxx = self.order['image_extents']['maxx']
        minx = self.order['image_extents']['minx']
        maxy = self.order['image_extents']['maxy']
        miny = self.order['image_extents']['miny']
        units = self.order['image_extents']['units']
        xdif = 0
        ydif = 0
        tot_size = 0

        # Special care needs to be taken around the antemeridian where the minx
        # could be larger than the maxx when dealing with decimal degrees
        if units == 'dd' and minx > maxx:
            xdif = 360 - minx + maxx
        elif minx > maxx:
            errors['Check X extents'] = 'Maximum X is less than minimum X'
        else:
            xdif = abs(maxx - minx)

        if miny > maxy:
            errors['Check Y extents'] = 'Maximum Y is less than minimum Y'
        else:
            ydif = abs(maxy - miny)

        if self.order['resize']:
            resize_units = self.order['resize']['pixel_size_units']
            pixel_size = self.order['resize']['pixel_size']
        else:
            resize_units = units
            # This is sensor/band dependant, but this should be ok for now
            if units == 'dd':
                pixel_size = 0.0002695
            else:
                pixel_size = 30

        # Have to convert in case the resize units does not match the extent units
        if resize_units != units:
            if units == 'dd':
                pixel_size /= 111317.254174397
            else:
                pixel_size *= 111317.254174397

        if xdif > pixel_size and ydif > pixel_size:
            tot_size = xdif * ydif / pixel_size ** 2
        else:
            errors['Size Error'] = 'Unable to calculate output size, check extent and resize parameters'

        if tot_size > self.size_thresh:
            errors['Size Error'] = 'Requested extents exceed size threshold'

        self._add_error('Extent Validation Error', errors)

    def _validate_role(self):
        """
        Not all processing products are available to everyone

        Exclude lists will need to be generated for each designated role
        in the system, then compared against the incoming order
        """
        pass
