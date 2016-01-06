""" ESPA order validator implemented with cerberus """

from cerberus import Validator

PROJECTIONS = {
    'aea' : {
      'name': {'type': 'string',
               'required': True,
               'allowed': ['aea']},

      'standard_parallel_1': {'type': 'float',
                              'min':-90.0,
                              'max': 90.0,
                              'required': True},

      'standard_parallel_2': {'type': 'float',
                              'min':-90.0,
                              'max': 90.0,
                              'required': True},

      'central_meridian': {'type': 'float',
                           'min':-180.0,
                           'max':180.0,
                           'required': True},

      'latitude_of_origin': {'type': 'float',
                             'min':-90.0,
                             'max':90.0,
                             'required': True},

      'false_easting': {'type': 'float',
                        'required': True},

      'false_northing': {'type': 'float',
                         'required': True}
    },

    'utm' : {

      'name': {'type': 'string',
               'required': True,
               'allowed': ['utm']},

      'zone': {'type': 'integer',
               'min': 1,
               'max': 60,
               'required': True},

      'zone_ns': {'type': 'string',
                  'allowed': ['north', 'south'],
                  'required': True}
    },

    'lonlat' : {'name': {'type': 'string',
                         'required': True,
                         'allowed': ['lonlat']}},

    'sinu' : {

      'name': {'type': 'string',
               'allowed': ['sinu'],
               'required': True},

      'central_meridian': {'type': 'float',
                           'min':-180.0,
                           'max':180.0,
                           'required': True},

      'false_easting': {'type': 'float',
                        'required': True},

      'false_northing': {'type': 'float',
                         'required': True}
    },

    'ps' : {
      'name': {'type': 'string',
               'allowed': ['ps'],
               'required': True},

      'longitudinal_pole': {'type': 'float',
                            'min': -180.0,
                            'max': 180.0,
                            'required': True},

      'latitude_true_scale': {'type': 'float',
                              'anyof': [{'min': -90.0, 'max': -60.0},
                                        {'min': 60.0, 'max': 90.0}],
                              'required': True}
    },
}

PRODUCTS = [
  'tm_sr', 'tm_toa', 'tm_l1',
  'etm_sr', 'etm_toa', 'etm_l1',
  'olitirs_sr', 'olitirs_toa', 'olitirs_l1',
  'oli_l1'
]

FORMATS = ['gtiff', 'hdf-eos2', 'envi']

RESAMPLING_METHODS = ['nn', 'bil', 'cc']

ORDER_SCHEMA = {
  'inputs': {'type': 'inputproducts'},
  'products': {'type': 'list', 'allowed': PRODUCTS},
  'projection': {'type': 'projection', 'allowed': [PROJECTIONS['aea'],
                                                   PROJECTIONS['utm'],
                                                   PROJECTIONS['lonlat'],
                                                   PROJECTIONS['sinu'],
                                                   PROJECTIONS['ps']]},
  'image_extents': {'type': 'string', 'dependencies': 'projection'},
  'format': {'type': 'string', 'allowed': FORMATS},
  'resize': {'type': 'integer'},
  'resampling_method': {'type': 'string', 'allowed': RESAMPLING_METHODS}
}


class OrderValidator(Validator):
    """ Custom validation for ESPA orders """

    def __init__(self, *args, **kwargs):
        """ construct a new validator """
        super(OrderValidator, self).__init__(*args, **kwargs)

    def _validate_type_projection(self, field, value):
        """ validation type for projections

        Args:
            field (str): Name of the field
            value: The value supplied to the field
        """
        if type(value) is not dict:
            self._error(field, 'projection must be a dictionary')
        if ('name' not in value or
                value['name'] not in globals()['projections'].keys()):
            self._error(field, 'cannot determine requested projection')
        else:
            projection = globals()['projections'][value['name']]
            self.validate(value, projection)

    def _validate_type_inputproducts(self, field, value):
        """ Validates input products """
        if not hasattr(value, '__iter__'):
            msg = 'inputs must be iterable, {0} found'.format(type(value))
            self._error(field, msg)

    def _validate_type_imageextents(self, field, value):
        """ Validates image extents """
        #north, south, east, west
        pass

def validate(order):
    """ performs validation for the supplied order

    Args:
        order (Order): The order to be validated

    Raises:
        ValidationException if the order is invalid
    """
    pass
