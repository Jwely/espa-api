import abc

import validictory
from validation_provider import ESPAOrderValidatorV0
from validation_schema import Version0Schema


class ValidationInterfaceV0(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self, order, username):
        """Validate a given order, make sure all parameters are good"""
        return

    @abc.abstractmethod
    def fetch_projections(self):
        """Return supported projections and their schemas"""
        return

    @abc.abstractmethod
    def fetch_formats(self):
        """Return supported file formats"""
        return

    @abc.abstractmethod
    def fetch_resampling(self):
        """Return supported resampling options"""
        return

    @abc.abstractmethod
    def fetch_order_schema(self):
        """Return the validation schema"""
        return

    @abc.abstractmethod
    def __call__(self):
        return


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
            validictory.validate(order, self.schema, fail_fast=False,
                                 validator_cls=ESPAOrderValidatorV0, required_by_default=False)
        except validictory.MultipleValidationError as e:
            return e
        except validictory.SchemaError as e:
            return e

    def fetch_projections(self):
        return self.schema.valid_params['projections']

    def fetch_formats(self):
        return self.schema.valid_params['formats']

    def fetch_resampling(self):
        return self.schema.valid_params['resampling_methods']

    def fetch_order_schema(self):
        return self.schema.request_schema

    __call__ = validate
