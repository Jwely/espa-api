""" Module to glue interfaces to implementations """

from api.providers.inventory import MockInventoryProvider
from api.providers.metrics import MockMetricsProvider
from api.providers.ordering import MockOrderingProvider
from api.providers.validation import MockValidationProvider
from api.providers.ordering.ordering_provider import OrderingProvider
from api.providers.validation import ValidationProvider
from api.providers.ordering.production_provider import ProductionProvider

class DefaultProviders(object):
    api_versions = {"versions":
                        {"0":
                            {"description": "First release of the ESPA API"}
                        }
                    }

    ordering = OrderingProvider()

    validation = ValidationProvider()

    metrics = MockMetricsProvider()

    inventory = MockInventoryProvider()

    production = ProductionProvider()

class MockProviders(object):
    ordering = MockOrderingProvider()

    validation = MockValidationProvider()

    metrics = MockMetricsProvider()

    inventory = MockInventoryProvider()
