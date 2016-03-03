import abc
import copy

import validictory
from validation_provider import OrderValidatorV0
from validation_schema import Version0Schema
from api.api_exceptions import ValidationException


class ValidationInterfaceV0(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self, order, username):
        """Validate a given order, make sure all parameters are good"""

    @abc.abstractmethod
    def fetch_projections(self):
        """Return supported projections and their schemas"""

    @abc.abstractmethod
    def fetch_formats(self):
        """Return supported file formats"""

    @abc.abstractmethod
    def fetch_resampling(self):
        """Return supported resampling options"""

    @abc.abstractmethod
    def fetch_order_schema(self):
        """Return the validation schema"""

    @abc.abstractmethod
    def __call__(self):
        pass


class MockValidationProvider(ValidationInterfaceV0):
    def validate(self, order, username):
        pass

    def fetch_projections(self):
        pass

    def fetch_formats(self):
        pass

    def fetch_resampling(self):
        pass

    def fetch_order_schema(self):
        pass

    __call__ = validate


class ValidationProvider(ValidationInterfaceV0):
    schema = Version0Schema()

    def validate(self, order, username):
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

    def fetch_projections(self):
        return copy.deepcopy(self.schema.valid_params['projections'])

    def fetch_formats(self):
        return copy.deepcopy(self.schema.valid_params['formats'])

    def fetch_resampling(self):
        return copy.deepcopy(self.schema.valid_params['resampling_methods'])

    def fetch_order_schema(self):
        return copy.deepcopy(self.schema.request_schema)

    __call__ = validate
