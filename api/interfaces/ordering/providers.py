""" Module to glue interfaces to implementations """

from api.providers.inventory.inventory_provider import MockInventoryProvider, InventoryProvider
from api.providers.metrics import MockMetricsProvider, MetricsProvider
from api.providers.ordering import MockOrderingProvider
from api.providers.ordering.ordering_provider import OrderingProvider
from api.providers.production.production_provider import ProductionProvider
from api.providers.validation import MockValidationProvider
from api.providers.validation import ValidationProvider


class DefaultProviders(object):
    api_versions = {"versions":
                        {"0":
                            {"description": "First release of the ESPA API"}
                        }
                    }

    ordering = OrderingProvider()

    validation = ValidationProvider()

    metrics = MetricsProvider()

    inventory = InventoryProvider()

    production = ProductionProvider()

class MockProviders(object):
    ordering = MockOrderingProvider()

    validation = MockValidationProvider()

    metrics = MockMetricsProvider()

    inventory = MockInventoryProvider()
