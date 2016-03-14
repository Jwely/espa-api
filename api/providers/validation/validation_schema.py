import api.domain.sensor as sn


class BaseValidationSchema(object):
    def __init__(self):
        self.formats = ['gtiff', 'hdf-eos2', 'envi']

        self.resampling_methods = ['nn', 'bil', 'cc']

        self.projections = {'aea': {'type': 'object',
                                    'properties': {'standard_parallel_1': {'type': 'number',
                                                                           'required': True,
                                                                           'minimum': -90,
                                                                           'maximum': 90},
                                                   'standard_parallel_2': {'type': 'number',
                                                                           'required': True,
                                                                           'minimum': -90,
                                                                           'maximum': 90},
                                                   'central_meridian': {'type': 'number',
                                                                        'required': True,
                                                                        'minimum': -180,
                                                                        'maximum': 180},
                                                   'latitude_of_origin': {'type': 'number',
                                                                          'required': True,
                                                                          'minimum': -90,
                                                                          'maximum': 90},
                                                   'false_easting': {'type': 'number',
                                                                     'required': True},
                                                   'false_northing': {'type': 'number',
                                                                      'required': True},
                                                   'datum': {'type': 'string',
                                                             'required': True,
                                                             'enum': ['wgs84', 'nad27', 'nad83']}}},
                            'utm': {'type': 'object',
                                    'properties': {'zone': {'type': 'integer',
                                                            'required': True,
                                                            'minimum': 1,
                                                            'maximum': 60},
                                                   'zone_ns': {'type': 'string',
                                                               'required': True,
                                                               'enum': ['north', 'south']}}},
                            'lonlat': {'type': 'null'},
                            'sinu': {'type': 'object',
                                     'properties': {'central_meridian': {'type': 'number',
                                                                         'required': True,
                                                                         'minimum': -180,
                                                                         'maximum': 180},
                                                    'false_easting': {'type': 'number',
                                                                      'required': True},
                                                    'false_northing': {'type': 'number',
                                                                       'required': True}}},
                            'ps': {'type': 'object',
                                   'properties': {'longitudinal_pole': {'type': 'number',
                                                                        'required': True,
                                                                        'minimum': -180,
                                                                        'maximum': 180},
                                                  'latitude_true_scale': {'type': 'number',
                                                                          'required': True,
                                                                          'abs_rng': (60, 90)}}}}

        self.extents = {'north': {'type': 'number',
                                  'required': True},
                        'south': {'type': 'number',
                                  'required': True},
                        'east': {'type': 'number',
                                 'required': True},
                        'west': {'type': 'number',
                                 'required': True},
                        'units': {'type': 'string',
                                  'required': True,
                                  'enum': ['dd', 'meters']}}

        self.resize = {'pixel_size': {'type': 'number',
                                      'required': True,
                                      'ps_dd_rng': (0.0002695, 0.0449155),
                                      'ps_meter_rng': (30, 5000)},
                       'pixel_size_units': {'type': 'string',
                                            'required': True,
                                            'enum': ['dd', 'meters']}}

        self.request_schema = {'type': 'object',
                               'set_ItemCount': ('inputs', 5000),
                               'properties': {'projection': {'properties': self.projections,
                                                             'type': 'object',
                                                             # 'enum_keys': self.projections.keys(),
                                                             'single_obj': True},
                                              'image_extents': {'extents': 200000000,
                                                                'type': 'object',
                                                                'properties': self.extents,
                                                                # 'enum_keys': self.extents.keys(),
                                                                'dependencies': ['projection']},
                                              'format': {'type': 'string',
                                                         'required': True,
                                                         'enum': self.formats},
                                              'resize': {'type': 'object',
                                                         'properties': self.resize,
                                                         'dependencies': ['projection']},
                                              'resampling_method': {'type': 'string',
                                                                    'enum': self.resampling_methods},
                                              'plot_statistics': {'type': 'boolean'}}}

        sensor_schema = self.build_sensor_schema()

        self.request_schema['properties'].update(sensor_schema)
        self.request_schema['oneormoreobjects'] = sensor_schema.keys()

        self.valid_params = {'formats': {'formats': self.formats},
                             'resampling_methods': {'resampling_methods': self.resampling_methods},
                             'projections': self.projections}

    @staticmethod
    def build_sensor_schema():
        sensor_reg = sn.SensorCONST.instances

        out_schema = {}
        for key in sensor_reg:
            out_schema[key] = {'type': 'object',
                               # 'enum_keys': ['inputs', 'products'],
                               'properties': {'inputs': {'type': 'array',
                                                         'required': True,
                                                         'ItemCount': 'inputs',
                                                         'uniqueItems': True,
                                                         'items': {'type': 'string',
                                                                   'pattern': sensor_reg[key][0]}},
                                              'products': {'type': 'array',
                                                           'uniqueItems': True,
                                                           'required': True,
                                                           'role_restricted': True,
                                                           'items': {'type': 'string',
                                                                     'enum': sn.instance(
                                                                         sensor_reg[key][2]).products}}}}

        return out_schema


class Version0Schema(BaseValidationSchema):
    def __init__(self):
        super(Version0Schema, self).__init__()
