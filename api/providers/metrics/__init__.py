import abc


class MetricsProviderInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def previous_month(self):
        pass


class MockMetricsProvider(MetricsProviderInterface):

    def previous_month(self):
        pass


class MetricsProvider(MetricsProviderInterface):

    def previous_month(self):
        pass
