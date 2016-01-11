import cerberus
from cerberus import Validator
# from api.providers.validation.schema import PROJECTIONS, FORMATS, RESAMPLING_METHODS, REQUEST_SCHEMA
from api.domain.sensor import available_products


class ValidationException(Exception):
    pass


class MockValidationProvider(Validator):
    pass
#     """
#     Mock validation provider using globals
#     Just for demonstration
#     """
#     def __init__(self, order=None):
#         super(MockValidationProvider, self).__init__()
#         self.order = order
#
#         self.val_formats = {'formats': FORMATS}
#         self.val_resampling = {'resampling_methods': RESAMPLING_METHODS}
#         self.val_projections = {proj['schema']['name']['allowed'][0]: proj['schema'] for proj in PROJECTIONS}
#
#     def __nonzero__(self):
#         return self.validate(self.order, REQUEST_SCHEMA)
#
#     def valid_projections(self):
#         return self.val_projections
#
#     def valid_formats(self):
#         return self.val_formats
#
#     def valid_resampling(self):
#         return self.val_resampling


class ValidationProvider(Validator):
    """
    Validation class for incoming orders
    """
    # TODO Build some informative error messages to give back due to validation issues
    def __init__(self, schema_cls, order=None, *args, **kwargs):
        try:
            super(ValidationProvider, self).__init__(schema=schema_cls.request_schema, *args, **kwargs)
        except Exception as e:
            print e
            pass
            # raise ValidationException(e)

        self.order = order
        self.schema_cls = schema_cls

        self.valid_params = self.schema_cls.valid_params

    def __call__(self, order):
        self.order = order

        try:
            return self.validate(self.order)
        except Exception as e:
            raise ValidationException(e)

    def _validate_scene_list(self, scenes):
        """
        Validate the scene list with the available products for a particular sensor
        """
        pass
