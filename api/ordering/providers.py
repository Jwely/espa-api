""" Module to glue interfaces to implementations """

from api.providers.inventory import MockInventoryProvider
from api.providers.metrics import MockMetricsProvider
from api.providers.ordering import MockOrderingProvider
from api.providers.validation import MockValidationProvider


class DefaultProviders(object):
    ordering = MockOrderingProvider()

    validation = MockValidationProvider()

    metrics = MockMetricsProvider()

    inventory = MockInventoryProvider()


class MockProviders(object):
    ordering = MockOrderingProvider()

    validation = MockValidationProvider()

    metrics = MockMetricsProvider()

    inventory = MockInventoryProvider()
