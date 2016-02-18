""" Module to glue interfaces to implementations """

from api.providers.inventory.inventory_provider import MockInventoryProvider, InventoryProvider
from api.providers.metrics import MockMetricsProvider, MetricsProvider
from api.providers.ordering import MockOrderingProvider
from api.providers.validation import MockValidationProvider, ValidationProvider
from api.providers.ordering.ordering_provider import OrderingProvider


class DefaultProviders(object):
    api_versions = {"versions":
                        {"0":
                            {"description": "demo access points for development"}
                        }
                    }

    ordering = OrderingProvider()

    validation = ValidationProvider()

    metrics = MetricsProvider()

    inventory = InventoryProvider()


class MockProviders(object):
    ordering = MockOrderingProvider()

    validation = MockValidationProvider()

    metrics = MockMetricsProvider()

    inventory = MockInventoryProvider()
