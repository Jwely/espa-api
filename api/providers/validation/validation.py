import cerberus
from cerberus import Validator
from api.providers.validation.schema import PROJECTIONS, FORMATS, RESAMPLING_METHODS, REQUEST_SCHEMA


class ValidationException(Exception):
    pass


class MockValidationProvider(Validator):
    """
    Mock validation provider using globals
    Just for demonstration
    """
    def __init__(self, order=None):
        super(MockValidationProvider, self).__init__()
        self.order = order

        self.val_formats = {'formats': FORMATS}
        self.val_resampling = {'resampling_methods': RESAMPLING_METHODS}
        self.val_projections = {proj['schema']['name']['allowed'][0]: proj['schema'] for proj in PROJECTIONS}

    def __nonzero__(self):
        return self.validate(self.order, REQUEST_SCHEMA)

    def valid_projections(self):
        return self.val_projections

    def valid_formats(self):
        return self.val_formats

    def valid_resampling(self):
        return self.val_resampling


class ValidationProvider(Validator):
    """
    Validation class for incoming orders
    """
    def __init__(self, order=None, *args, **kwargs):
        try:
            super(ValidationProvider, self).__init__(*args, **kwargs)
        except Exception as e:
            pass
            # raise ValidationException(e)

        self.order = order
        # self.val_schema = kwargs.get('schema')

        self.valid_formats = {'formats': self.schema['customizations']['schema']['format']['oneof']}
        self.valid_resampling = {'resampling_methods': self.schema['customizations']['schema']['resampling']['oneof']}
        self.valid_projections = {proj['schema']['name']['allowed'][0]: proj['schema'] for proj in
                                  self.schema['customizations']['schema']['projection']['oneof']}

    def __call__(self, order):
        self.order = order

        try:
            return self.validate(self.order)
        except Exception as e:
            raise ValidationException(e)
