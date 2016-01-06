from cerberus import Validator
from api.providers.validation.schema import PROJECTIONS, FORMATS, RESAMPLING_METHODS, REQUEST_SCHEMA


class MockValidationProvider(Validator):
    def __init__(self, order=None):
        super(MockValidationProvider, self).__init__()
        self.order = order

        self.val_formats = {'formats': FORMATS}
        self.val_resampling = {'resampling_methods': RESAMPLING_METHODS}
        self.val_projections = {proj['schema']['name']['allowed'][0]: proj['schema'] for proj in PROJECTIONS}

    def __nonzero__(self):
        return self.validate(self.order, REQUEST_SCHEMA)

    def valid_projections(self):
        return self.val_projections

    def valid_formats(self):
        return self.val_formats

    def valid_resampling(self):
        return self.val_resampling



