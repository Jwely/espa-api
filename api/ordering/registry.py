""" Module to glue interfaces to implementations """

from api.providers.ordering import MockOrderingProvider
from api.providers.validation import MockValidationProvider
from api.providers.metrics import MockMetricsProvider
from api.providers.inventory import MockInventoryProvider

ordering = MockOrderingProvider

validation = MockValidationProvider

metrics = MockMetricsProvider

inventory = MockInventoryProvider
