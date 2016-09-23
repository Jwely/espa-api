""" Module to glue interfaces to implementations """

from api.providers.inventory.inventory_provider import MockInventoryProvider, InventoryProvider
from api.providers.metrics import MockMetricsProvider, MetricsProvider
from api.providers.ordering import MockOrderingProvider
from api.providers.ordering.ordering_provider import OrderingProvider
from api.providers.production.production_provider import ProductionProvider
from api.providers.reporting.reporting_provider import ReportingProvider
from api.providers.validation import MockValidationProvider
from api.providers.validation.validictory import ValidationProvider
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.providers.administration.administration_provider import AdministrationProvider


class DefaultProviders(object):

    ordering = OrderingProvider()

    validation = ValidationProvider()

    metrics = MetricsProvider()

    inventory = InventoryProvider()

    production = ProductionProvider()

    configuration = ConfigurationProvider()

    reporting = ReportingProvider()

    administration = AdministrationProvider()


class MockProviders(object):
    ordering = MockOrderingProvider()

    validation = MockValidationProvider()

    metrics = MockMetricsProvider()

    inventory = MockInventoryProvider()
