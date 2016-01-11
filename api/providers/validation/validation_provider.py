from cerberus import Validator
from api.domain.sensor import available_products


class ValidationException(Exception):
    pass


class ValidationProvider(Validator):
    """
    Validation class for incoming orders
    """
    # TODO Build some informative error messages to give back due to validation issues
    def __init__(self, schema_cls, *args, **kwargs):
        try:
            super(ValidationProvider, self).__init__(schema=schema_cls.request_schema, *args, **kwargs)
        except Exception as e:
            print e
            pass
            # raise ValidationException(e)

        self.schema_cls = schema_cls

        self.valid_params = self.schema_cls.valid_params

    def __call__(self, order):
        try:
            self._validate_scene_list(order['inputs'], order['products'])
            return self.validate(order)
        except Exception as e:
            raise ValidationException(e)

    def _validate_scene_list(self, scenes, req_prods):
        """
        Validate the scene list with the available products for a particular sensor
        """
        # for scene in scenes:
        #     avail_prods = available_products(scene)
        pass
