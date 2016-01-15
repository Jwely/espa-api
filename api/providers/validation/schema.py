from api.domain.sensor import instance


def populate_products():
    """
    Build a complete list of all available products that are available for all supported sensors

    This pulls straight from sensor.py, which is centrally being used to keep track of supported
    sensors

    :return: List of supported products
    """
    # Technically all the MODIS products could be wrapped up in two prefixes, but for completeness
    # let's check everything that is supposed to be supported
    sensor_acqids = {'.A2000072.h02v09.005.2008237032813': ['MOD09A1', 'MOD09GA', 'MOD09GQ', 'MOD09Q1',
                                                            'MYD09A1', 'MYD09GA', 'MYD09GQ', 'MYD09Q1',
                                                            'MOD13A1', 'MOD13A2', 'MOD13A3', 'MOD13Q1',
                                                            'MYD13A1', 'MYD13A2', 'MYD13A3', 'MYD13Q1'],
                     '2181092013069PFS00': ['LT4', 'LT5', 'LE7', 'LO8', 'LC8']}

    all_prods = []
    for acq in sensor_acqids:
        for prefix in sensor_acqids[acq]:
            prods = instance('{}{}'.format(prefix, acq)).products
            for prod in prods:
                if prod not in all_prods:
                    all_prods.append(prod)

    return all_prods


class BaseValidationSchema(object):
    """
    Provides the base order validation schema to be passed to the Cerberus module
    and the valid parameters associated with the schema

    This is meant to be inherited into major version change schemas, with changes
    overriding the base object
    """

    formats = ['gtiff', 'hdf-eos2', 'envi']

    resampling_methods = ['nn', 'bil', 'cc']

    image_extents = [{'type': 'dict',
                      'schema': {'minx': {'type': 'float',
                                          'required': True},
                                 'maxx': {'type': 'float',
                                          'required': True},
                                 'miny': {'type': 'float',
                                          'required': True},
                                 'maxy': {'type': 'float',
                                          'required': True},
                                 'units': {'type': 'string',
                                           'required': True,
                                           'allowed': ['meters']}}},
                     {'type': 'dict',
                      'schema': {'minx': {'type': 'float',
                                          'min': -180,
                                          'max': 180,
                                          'required': True},
                                 'maxx': {'type': 'float',
                                          'min': -180,
                                          'max': 180,
                                          'required': True},
                                 'miny': {'type': 'float',
                                          'min': -90,
                                          'max': 90,
                                          'required': True},
                                 'maxy': {'type': 'float',
                                          'min': -90,
                                          'max': 90,
                                          'required': True},
                                 'units': {'type': 'string',
                                           'required': True,
                                           'allowed': ['dd']}}}]

    resize = [{'type': 'dict',
               'schema': {'pixel_size': {'type': 'float',
                                         'min': 30.0,
                                         'max': 1000.0,
                                         'required': True},
                          'pixel_size_units': {'type': 'string',
                                               'allowed': ['meters'],
                                               'required': True}}},
              {'type': 'dict',
               'schema': {'pixel_size': {'type': 'float',
                                         'min': 0.0002695,
                                         'max': 0.0089831,
                                         'required': True},
                          'pixel_size_units': {'type': 'string',
                                               'allowed': ['dd'],
                                               'required': True}}}]

    products = populate_products()

                    # Albers
    projections = [{'type': 'dict',
                    'schema': {'name': {'type': 'string',
                                        'required': True,
                                        'allowed': ['aea']},
                               'standard_parallel_1': {'type': 'float',
                                                       'required': True,
                                                       'min': -90.0,
                                                       'max': 90.0},
                               'standard_parallel_2': {'type': 'float',
                                                       'required': True,
                                                       'min': -90.0,
                                                       'max': 90.0},
                               'central_meridian': {'type': 'float',
                                                    'required': True,
                                                    'min': -180.0,
                                                    'max': 180.0},
                               'latitude_of_origin': {'type': 'float',
                                                      'required': True,
                                                      'min': -90.0,
                                                      'max': 90.0},
                               'false_easting': {'type': 'float',
                                                 'required': True},
                               'false_northing': {'type': 'float',
                                                  'required': True}}},
                   # UTM
                   {'type': 'dict',
                    'schema': {'name': {'type': 'string',
                                        'required': True,
                                        'allowed': ['utm']},
                               'zone': {'type': 'integer',
                                        'required': True,
                                        'min': 1,
                                        'max': 60},
                               'zone_ns': {'type': 'string',
                                           'required': True,
                                           'allowed': ['north', 'south']}}},
                   # Geographic
                   {'type': 'dict',
                    'schema': {'name': {'type': 'string',
                                        'required': True,
                                        'allowed': ['lonlat']}}},
                   # Sinusoidal
                   {'type': 'dict',
                    'schema': {'name': {'type': 'string',
                                        'required': True,
                                        'allowed': ['sinu']},
                               'central_meridian': {'type': 'float',
                                                    'required': True,
                                                    'min': -180.0,
                                                    'max': 180.0},
                               'false_easting': {'type': 'float',
                                                 'required': True},
                               'false_northing': {'type': 'float',
                                                  'required': True}}},
                   # Polar
                   {'type': 'dict',
                    'schema': {'name': {'type': 'string',
                                        'required': True,
                                        'allowed': ['ps']},
                               'longitudinal_pole': {'type': 'float',
                                                     'required': True,
                                                     'min': -180.0,
                                                     'max': 180.0},
                               'latitude_true_scale': {'type': 'float',
                                                       'required': True,
                                                       'anyof': [{'min': -90.0, 'max': -60.0},
                                                                 {'min': 60.0, 'max': 90.0}]}}}]

    # DEVELOPER_OPTIONS = {'keep_directory': {'type': 'boolean'},
    #                      'keep_intermediate_data': {'type': 'boolean'},
    #                      'keep_log': {'type': 'boolean'}}

    request_schema = {'inputs': {'type': 'list',
                                 'required': True,
                                 'schema': {'type': 'string'}},
                      'products': {'type': 'list',
                                   'required': True,
                                   'allowed': products},
                      'projection': {'type': 'dict',
                                     'required': False,
                                     'oneof': projections},
                      'image_extents': {'type': 'dict',
                                        'required': False,
                                        # 'dependencies': ['projection'],
                                        'oneof': image_extents},
                      'format': {'type': 'string',
                                 'required': False,
                                 'allowed': formats},
                      'resize': {'type': 'dict',
                                 'required': False,
                                 'oneof': resize},
                      'resampling_method': {'type': 'string',
                                            'required': False,
                                            'allowed': resampling_methods}}

    valid_params = {'formats': {'formats': formats},
                    'resampling_methods': {'resampling_methods': resampling_methods},
                    'projections': {proj['schema']['name']['allowed'][0]: proj['schema'] for proj in
                                    projections}}


class Version0Schema(BaseValidationSchema):
    pass
