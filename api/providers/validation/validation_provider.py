import cerberus
from api.domain.sensor import instance, available_products, ProductNotImplemented


class ValidationException(Exception):
    pass


class ValidationProvider(object):
    """
    Validation class for incoming orders against a given schema
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

        print self.errors
        if not self.errors:
            return True
        else:
            return False

    def __call__(self, *args, **kwargs):
        return self.validate(*args, **kwargs)

    def _validate_orderstruct(self):
        self.validator(self.order)

        if self.validator.errors:
            self._add_error('Schema Error', self.validator.errors)

    def _validate_scene_list(self):
        """
        Validate the scene list with the available products for a particular sensor
        """
        errors = {}

        # Get all available products sorted by sensor
        try:
            results = available_products(self.order['inputs'])
        except Exception as e:
            raise ValidationException(e)

        if 'not_implemented' in results:
            errors['not_implemented'] = results['not_implemented']

        for scene in self.order['inputs']:
            try:
                avail_prods = instance(scene)
                diff = list(set(self.order['products']) - set(avail_prods.products))
                if diff:
                    errors[scene] = '{} not available'.format(', '.join(diff))
            except ProductNotImplemented as e:
                errors[scene] = e

        if errors:
            self._add_error('Requested Products Error', errors)

    def _validate_sizethresh(self):
        xdif = abs(self.order['image_extents']['maxx'] - self.order['image_extents']['minx'])
        ydif = abs(self.order['image_extents']['maxy'] - self.order['image_extents']['miny'])
        tot_size = xdif * ydif / self.order['resize']

        if tot_size > self.size_thresh:
            self._add_error('Size Error', 'Requested extents exceed size threshold')

    def _validate_imageextents(self):
        msgs = []
        if self.order['image_extents']['minx'] > self.order['image_extents']['maxx']:
            msgs.append('Max X extent is less than minimum X')

        if self.order['projection'] and self.order['image_extents']:
            return True
        else:
            return False

    def _validate_role(self):
        pass
