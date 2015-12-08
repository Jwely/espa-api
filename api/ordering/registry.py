from providers.ordering import DefaultOrderingProvider
from providers.validation import CerberusValidationProvider
from providers.metrics import PostgresMetricsProvider

ordering = DefaultOrderingProvider

# provide cerberus schema here and new the object up??
validation = CerberusValidationProvider

metrics = PostgresMetricsProvider
