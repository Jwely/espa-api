import api.domain.sensor as sn


class BaseValidationSchema(object):
    """
    Provides the base order validation schema to be passed to the Cerberus module
    and the valid parameters associated with the schema

    This is meant to be inherited into major version change schemas, with changes
    mutating or overriding the base object as necessary
    """

    def __init__(self):
        self.formats = ['gtiff', 'hdf-eos2', 'envi']

        self.resampling_methods = ['nn', 'bil', 'cc']

        self.image_extents = {'meters': {'north': {'type': 'float',
                                                   'required': True},
                                         'south': {'type': 'float',
                                                   'required': True},
                                         'east': {'type': 'float',
                                                  'required': True},
                                         'west': {'type': 'float',
                                                  'required': True},
                                         'units': {'type': 'string',
                                                   'required': True,
                                                   'allowed': ['meters']}},
                              'dd': {'east': {'type': 'float',
                                              'min': -180,
                                              'max': 180,
                                              'required': True},
                                     'west': {'type': 'float',
                                              'min': -180,
                                              'max': 180,
                                              'required': True},
                                     'north': {'type': 'float',
                                               'min': -90,
                                               'max': 90,
                                               'required': True},
                                     'south': {'type': 'float',
                                               'min': -90,
                                               'max': 90,
                                               'required': True},
                                     'units': {'type': 'string',
                                               'required': True,
                                               'allowed': ['dd']}}}

        self.resize = {'meters': {'pixel_size': {'type': 'float',
                                                 'min': 30.0,
                                                 'max': 1000.0,
                                                 'required': True},
                                  'pixel_size_units': {'type': 'string',
                                                       'allowed': ['meters'],
                                                       'required': True}},
                       'dd': {'pixel_size': {'type': 'float',
                                             'min': 0.0002695,
                                             'max': 0.0089831,
                                             'required': True},
                              'pixel_size_units': {'type': 'string',
                                                   'allowed': ['dd'],
                                                   'required': True}}}

        # Albers
        self.projections = {'aea': {'name': {'type': 'string',
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
                                                       'required': True},
                                    'datum': {'type': 'string',
                                              'allowed': ['wgs84', 'nad27', 'nad83'],
                                              'required': True}},
                            # UTM
                            'utm': {'name': {'type': 'string',
                                             'required': True,
                                             'allowed': ['utm']},
                                    'zone': {'type': 'integer',
                                             'required': True,
                                             'min': 1,
                                             'max': 60},
                                    'zone_ns': {'type': 'string',
                                                'required': True,
                                                'allowed': ['north', 'south']}},
                            # Geographic
                            'lonlat': {'name': {'type': 'string',
                                                'required': True,
                                                'allowed': ['lonlat']}},
                            # Sinusoidal
                            'sinu': {'name': {'type': 'string',
                                              'required': True,
                                              'allowed': ['sinu']},
                                     'central_meridian': {'type': 'float',
                                                          'required': True,
                                                          'min': -180.0,
                                                          'max': 180.0},
                                     'false_easting': {'type': 'float',
                                                       'required': True},
                                     'false_northing': {'type': 'float',
                                                        'required': True}},
                            # Polar
                            'ps': {'name': {'type': 'string',
                                            'required': True,
                                            'allowed': ['ps']},
                                   'longitudinal_pole': {'type': 'float',
                                                         'required': True,
                                                         'min': -180.0,
                                                         'max': 180.0},
                                   'latitude_true_scale': {'type': 'float',
                                                           'required': True,
                                                           'anyof': [{'min': -90.0, 'max': -60.0},
                                                                     {'min': 60.0, 'max': 90.0}]}}}

        # DEVELOPER_OPTIONS = {'keep_directory': {'type': 'boolean'},
        #                      'keep_intermediate_data': {'type': 'boolean'},
        #                      'keep_log': {'type': 'boolean'}}

        self.request_schema = {'projection': {'type': 'dict',
                                              'required': True},
                               'image_extents': {'type': 'dict',
                                                 'required': True},
                               'format': {'type': 'string',
                                          'required': True,
                                          'allowed': self.formats},
                               'resize': {'type': 'dict',
                                          'required': True},
                               'resampling_method': {'type': 'string',
                                                     'required': True,
                                                     'allowed': self.resampling_methods},
                               'plot_statistics': {'type': 'boolean',
                                                   'required': True}}

        sensorprod_schemas = self.build_sensorprods_schema()

        for prod in sensorprod_schemas:
            self.request_schema[prod] = sensorprod_schemas[prod]

        self.valid_params = {'formats': {'formats': self.formats},
                             'resampling_methods': {'resampling_methods': self.resampling_methods},
                             'projections': self.projections}

    @staticmethod
    def build_sensorprods_schema():
        """
        Build the dynamic sensor/product schemas
        These are built based on the end point classes inside of sensor.py

        :return: dictionary of schemas
        """
        out_schemas = {}

        li = []
        for acq in sn.TEST_STRINGS:
            for prefix in sn.TEST_STRINGS[acq]:
                li.append('{}{}'.format(prefix, acq))

        results = sn.available_products(li)

        for sensor, prods in results.items():
            out_schemas[sensor] = {'type': 'dict',
                                   'required': False,
                                   'schema': {'inputs': {'type': 'list',
                                                         'required': True},
                                              'products': {'type': 'list',
                                                           'required': True,
                                                           'allowed': prods['outputs']}}}

        return out_schemas


class Version0Schema(BaseValidationSchema):
    def __init__(self):
        super(Version0Schema, self).__init__()
