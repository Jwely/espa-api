import abc


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
