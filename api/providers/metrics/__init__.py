import abc


class MetricsProviderInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def collect(self, order):
        pass


class MockMetricsProvider(MetricsProviderInterface):

    def collect(self, order):
        pass


class MetricsProvider(MetricsProviderInterface):

    def collect(self, order):
        pass
