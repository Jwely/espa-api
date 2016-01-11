from api.domain.sensor import available_products


class BaseValidationSchema(object):
    """
    Provides the base order validation schema to be passed to the Cerberus module
    and the valid parameters associated with the schema

    This is meant to be inherited into major version change schemas
    """

    formats = ['gtiff', 'hdf-eos2', 'envi']

    resampling_methods = ['nn', 'bil', 'cc']

    image_extents = [{'type': 'dict',
                      'schema': {'minx': {'type': 'float',
                                          'required': False,
                                          'dependencies': ['maxx', 'miny', 'maxy']},
                                 'maxx': {'type': 'float',
                                          'required': False,
                                          'dependencies': ['minx', 'miny', 'maxy']},
                                 'miny': {'type': 'float',
                                          'required': False,
                                          'dependencies': ['maxx', 'minx', 'maxy']},
                                 'maxy': {'type': 'float',
                                          'required': False,
                                          'dependencies': ['maxx', 'minx', 'miny']}}}]

    products = ['include_lst', 'include_solr', 'include_source_data',
                'include_source_metadata', 'include_cfmask', 'include_customized_source_data',
                'include_sr_evi', 'include_sr_msavi', 'include_sr_nbr',
                'include_sr_nbr2', 'include_sr_ndmi', 'include_sr_ndvi',
                'include_sr_savi', 'include_sr', 'include_sr_thermal',
                'include_sr_toa']

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
                                        'dependencies': ['projection'],
                                        'allof': image_extents},
                      'format': {'type': 'string',
                                 'required': False,
                                 'allowed': formats},
                      'resize': {'type': 'float',
                                 'required': False},
                      'resampling_method': {'type': 'string',
                                            'required': False,
                                            'allowed': resampling_methods}}

    valid_params = {'formats': {'formats': formats},
                    'resampling_methods': {'resampling_methods': resampling_methods},
                    'projections': {proj['schema']['name']['allowed'][0]: proj['schema'] for proj in
                                    projections}}


class Version0Schema(BaseValidationSchema):
    pass
