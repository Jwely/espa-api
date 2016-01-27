# TODO Look at maybe making the actual validation logic more generic and create a translation class
# TODO that pulls the appropriate data out of the schema/order to populate the required fields for
# TODO validation, this would better support future schema changes

import cerberus
import api.domain.sensor as sn
import api.providers.ordering as ordering


class ValidationException(Exception):
    pass


class ValidationProvider(object):
    """
    Validation class for incoming orders
    """
    def __init__(self, schema_cls,  size_thresh=200000000, *args, **kwargs):
        self.validator = cerberus.Validator()
        self.schema_cls = schema_cls()
        # self.userid = userid

        self.schema = self.schema_cls.request_schema
        self.valid_params = self.schema_cls.valid_params

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

        methods = dir(self)

        # Validate schemas first, then everything else
        # TODO look at organizing this better
        nonschema_methods = []
        for method in methods:
            if ('_validate_' and '_schema' in method) and callable(getattr(self, method)):
                func = getattr(self, method)
                func()
            elif '_validate_' in method and callable(getattr(self, method)):
                nonschema_methods.append(method)

        if not self.errors:
            for method in nonschema_methods:
                func = getattr(self, method)
                func()
        else:
            self._add_error('General Error', 'Schema errors must be fixed before validation can finish')

        # For my sanity right now in testing
        print self.errors

        if self.errors:
            return False
        else:
            return True

    def __call__(self, *args, **kwargs):
        return self.validate(*args, **kwargs)

    def _validate_order_schema(self):
        """
        Validate the incoming order structure against the schema
        the class was initialized with

        Uses the cerberus module to perform the actual validation
        and writes any cerberus errors to the class errors dict
        """
        self.validator(self.order, self.schema)

        if self.validator.errors:
            self._add_error('order_schema', self.validator.errors)

    def _validate_projection_schema(self):
        """
        Validates a given projection against supported types

        Uses the cerberus validator class along with the projection schema
        from the schema class
        """
        projs = self.schema_cls.projections

        if 'projection' not in self.order or not self.order['projection']:
            return

        if 'name' not in self.order['projection'] or self.order['projection']['name'] not in projs:
            self._add_error('projection_schema', 'Valid projection names are: {}'.format(', '.join(projs.keys())))
            return

        self.validator(self.order['projection'], projs[self.order['projection']['name']])

        if self.validator.errors:
            self._add_error('projection_schema', self.validator.errors)

    # def _validate_scene_lists(self):
    #     """
    #     Validate the scene list and requested sensors with the available products
    #
    #     Uses the sensor.py module to gather the available processing products for the
    #     given sensors
    #
    #     Writes any errors to the class errors dict
    #     """
    #     # TODO add in role based restrictions to requested products
    #     errors = {}
    #
    #     results = sn.available_products(self.order['inputs'])
    #
    #     if 'not_implemented' in results:
    #         errors['Sensor ID Not Recognized'] = results['not_implemented']
    #         results.pop('not_implemented', None)
    #
    #     supported_prods = []
    #     for sensor in results:
    #         supported_prods.extend(results[sensor]['outputs'])
    #
    #     unsupported = list(set(self.order['products']) - set(supported_prods))
    #
    #     if unsupported:
    #         errors['Unsupported Product'] = unsupported
    #
    #     if errors:
    #         self._add_error('scene_list', errors)

    def _validate_image_extents_schema(self):
        """
        Validates the extent parameters to make sure they are the
        correct data types and fall within the valid ranges

        Uses the cerberus validator class along with the image_extent schema
        from the schema class
        """
        errors = {}

        exts = self.schema_cls.image_extents

        if 'image_extents' not in self.order or not self.order['image_extents']:
            return
        elif 'projection' not in self.order or not self.order['projection']:
            errors['Projection Error'] = 'You must specify a projection to use image extents'

        if 'units' not in self.order['image_extents'] or self.order['image_extents']['units'] not in exts:
            errors['Units Error'] = 'Valid units are: {}'.format(', '.join(exts.keys()))

        if errors:
            self._add_error('image_extents_schema', errors)
        else:
            self.validator(self.order['image_extents'], exts[self.order['image_extents']['units']])

            if self.validator.errors:
                self._add_error('image_extents_schema', self.validator.errors)

    def _validate_image_extents(self):
        """
        Verifies that the requested image extents are valid

        Coordinates given should make sense based on unit type
        maxx > minx
        maxy > miny

        Total number of pixels do not exceed a processing threshold
        """
        if 'image_extents_schema' in self.errors or not self.order['image_extents']:
            return

        errors = {}

        maxx = self.order['image_extents']['east']
        minx = self.order['image_extents']['west']
        maxy = self.order['image_extents']['north']
        miny = self.order['image_extents']['south']
        extent_units = self.order['image_extents']['units']
        xdif = 0
        ydif = 0
        tot_size = 0

        if self.order['projection'] and self.order['projection']['name'] == 'lonlat':
            if extent_units != 'dd':
                errors['Units Error'] = 'Must use decimal degrees (dd) for geographic projection'

        # Special care needs to be taken around the antemeridian where the minx
        # could be larger than the maxx when dealing with decimal degrees
        # the maxx value will need to be converted to a positive value > 180
        # before the backend warp command is executed
        if extent_units == 'dd' and minx > 170 and -170 > maxx:
            xdif = 360 - minx + maxx
        elif minx > maxx:
            errors['Check East/West extents'] = 'Easterly value is less than the Westerly value'
        else:
            xdif = abs(maxx - minx)

        if miny > maxy:
            errors['Check Y extents'] = 'Northerly value is less than the Southerly value'
        else:
            ydif = abs(maxy - miny)

        if self.order['resize']:
            resize_units = self.order['resize']['pixel_size_units']
            pixel_size = self.order['resize']['pixel_size']
        else:
            resize_units = extent_units
            # This is sensor/band dependant, but this should be ok for now
            if extent_units == 'dd':
                pixel_size = 0.0002695
            else:
                pixel_size = 30

        # Have to convert in case the resize units does not match the extent units
        # Have to allow for extents to be given in dd, even when the projection is meters
        if resize_units != extent_units:
            if extent_units == 'dd':
                pixel_size /= 111317.254174397
            else:
                pixel_size *= 111317.254174397

        if xdif > pixel_size and ydif > pixel_size:
            tot_size = xdif * ydif / pixel_size ** 2
        else:
            errors['Size Error'] = 'Unable to verify output size, check extent and resize parameters'

        if tot_size > self.size_thresh:
            errors['Size Error'] = 'Total pixels requested exceeds size threshold'
        elif tot_size <= 0:
            errors['Size Error'] = 'Error calculating total pixels, check extent and resize parameters'

        if errors:
            self._add_error('image_extents', errors)

    def _validate_resize(self):
        """
        Validate the pixel resizing parameters
        """
        errors = {}
        if not self.order['resize'] or 'resize_schema' in self.errors:
            pass
        elif not self.order['projection']:
            if self.order['resize']['pixel_size_units'] != 'meters':
                errors['Units Error'] = 'Must use meters when no projection is specified'
        elif self.order['projection']['name'] == 'lonlat':
            if self.order['resize']['pixel_size_units'] != 'dd':
                errors['Units Error'] = 'Must use decimal degrees with geographic projection'
        elif self.order['resize']['pixel_size_units'] != 'meters':
                errors['Units Error'] = 'Must use meters with supported non-geographic projections'

        if errors:
            self._add_error('resize', errors)

    def _validate_resize_schema(self):
        """
        Validates a given resize parameters structure

        Uses the cerberus validator class along with the resize schema
        from the schema class
        """
        resize = self.schema_cls.resize

        if 'resize' not in self.order or not self.order['resize']:
            return

        if 'pixel_size_units' not in self.order['resize'] or self.order['resize']['pixel_size_units'] not in resize:
            self._add_error('resize_schema', 'Valid resize units are: {}'.format(', '.join(resize.keys())))
            return

        self.validator(self.order['resize'], resize[self.order['resize']['pixel_size_units']])

        if self.validator.errors:
            self._add_error('resize_schema', self.validator.errors)

    def _validate_role(self):
        """
        Not all processing products are available to everyone

        Exclude lists will need to be generated for each designated role
        in the system, then compared against the incoming order
        """
        pass
