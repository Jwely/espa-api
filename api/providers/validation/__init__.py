import abc
import copy

import validictory
from validation_provider import OrderValidatorV0
from validation_schema import Version0Schema
from api import ValidationException
from api.domain import sensor


class ValidationInterfaceV0(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self, order, username):
        """Validate a given order, make sure all parameters are good"""
        return order

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
        """
        Validate an incoming order to make sure everything is kosher

        :param order: incoming order dict
        :param username: username associated with the order
        :return: validated order
        """
        order = copy.deepcopy(order)
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

        return self.massage_formatting(order)

    @staticmethod
    def massage_formatting(order):
        """
        To avoid complications down the line, we need to ensure proper case formatting
        on the order, while still being somewhat case agnostic

        :param order: incoming order after validation
        :return: order with the inputs reformatted
        """
        prod_keys = sensor.SensorCONST.instances.keys()

        for key in order:
            if key in prod_keys:
                item1 = order[key]['inputs'][0]

                prod = sensor.instance(item1)

                if isinstance(prod, sensor.Landsat):
                    order[key]['inputs'] = [s.upper() for s in order[key]['inputs']]
                elif isinstance(prod, sensor.Modis):
                    order[key]['inputs'] = ('.'.join([p[0].upper(),
                                                      p[1].upper(),
                                                      p[2].lower(),
                                                      p[3],
                                                      p[4]]) for p in [s.split('.') for s in order[key]['inputs']])

        return order

    def fetch_projections(self):
        """
        Pass along projection information
        :return: dict
        """
        return copy.deepcopy(self.schema.valid_params['projections'])

    def fetch_formats(self):
        """
        Pass along valid file formats
        :return: dict
        """
        return copy.deepcopy(self.schema.valid_params['formats'])

    def fetch_resampling(self):
        """
        Pass along valid resampling options
        :return: dict
        """
        return copy.deepcopy(self.schema.valid_params['resampling_methods'])

    def fetch_order_schema(self):
        """
        Pass along the schema used for validation
        :return: dict
        """
        return copy.deepcopy(self.schema.request_schema)

    __call__ = validate
