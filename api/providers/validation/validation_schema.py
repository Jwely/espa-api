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
                                  'dependencies': ['north', 'south', 'east', 'west', 'units']},
                        'south': {'type': 'number',
                                  'dependencies': ['north', 'south', 'east', 'west', 'units']},
                        'east': {'type': 'number',
                                 'dependencies': ['north', 'south', 'east', 'west', 'units']},
                        'west': {'type': 'number',
                                 'dependencies': ['north', 'south', 'east', 'west', 'units']},
                        'units': {'type': 'string',
                                  'dependencies': ['north', 'south', 'east', 'west', 'units'],
                                  'enum': ['dd', 'meters']}}

        self.resize = {'pixel_size': {'type': 'number',
                                      'dependencies': ['pixel_size', 'pixel_size_units']},
                       'pixel_size_units': {'type': 'string',
                                            'dependencies': ['pixel_size', 'pixel_size_units'],
                                            'enum': ['dd', 'meters']}}

        self.request_schema = {'type': 'object',
                               'properties': {'projection': {'properties': self.projections,
                                                             'type': 'object',
                                                             'single_obj': True,
                                                             'enum_keys': self.projections.keys()},
                                              'image_extents': {'extents': 200000000,
                                                                'properties': self.extents,
                                                                'enum_keys': self.extents.keys(),
                                                                'dependencies': 'projection'},
                                              'format': {'type': 'string',
                                                         'required': True,
                                                         'enum': self.formats},
                                              'resize': {'type': 'object',
                                                         'properties': self.resize,
                                                         'dependencies': 'projection'},
                                              'resampling_method': {'type': 'string',
                                                                    'enum': self.resampling_methods},
                                              'plot_statistics': {'type': 'boolean'}}}

        sensor_schema = self.build_sensor_schema()

        self.request_schema['properties'].update(sensor_schema)
        self.request_schema['oneormore'] = sensor_schema.keys()

        self.valid_params = {'formats': {'formats': self.formats},
                             'resampling_methods': {'resampling_methods': self.resampling_methods},
                             'projections': self.projections}

    @staticmethod
    def build_sensor_schema():
        # acq_strings = {'.A2000072.h02v09.005.2008237032813': ['MOD09A1', 'MOD09GA', 'MOD09GQ', 'MOD09Q1',
        #                                                       'MYD09A1', 'MYD09GA', 'MYD09GQ', 'MYD09Q1',
        #                                                       'MOD13A1', 'MOD13A2', 'MOD13A3', 'MOD13Q1',
        #                                                       'MYD13A1', 'MYD13A2', 'MYD13A3', 'MYD13Q1'],
        #                '2181092013069PFS00': ['LT4', 'LT5', 'LE7', 'LO8', 'LC8']}

        sensor_reg = {'tm4': (r'^lt4\d{3}\d{3}\d{4}\d{3}[a-z]{3}[a-z0-9]{2}$',
                              'LT42181092013069PFS00'),
                      'tm5': (r'^lt5\d{3}\d{3}\d{4}\d{3}[a-z]{3}[a-z0-9]{2}$',
                              'LT52181092013069PFS00'),
                      'etm7': (r'^le7\d{3}\d{3}\d{4}\d{3}\w{3}.{2}$',
                               'LE72181092013069PFS00'),
                      'olitirs8': (r'^lc8\d{3}\d{3}\d{4}\d{3}\w{3}.{2}$',
                                   'LC82181092013069PFS00'),
                      'oli8': (r'^lo8\d{3}\d{3}\d{4}\d{3}\w{3}.{2}$',
                               'LO82181092013069PFS00'),
                      'mod09a1': (r'^mod09a1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'mod09a1.A2000072.h02v09.005.2008237032813'),
                      'mod09ga': (r'^mod09ga\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'mod09ga.A2000072.h02v09.005.2008237032813'),
                      'mod09gq': (r'^mod09gq\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'mod09gq.A2000072.h02v09.005.2008237032813'),
                      'mod09q1': (r'^mod09q1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'mod09q1.A2000072.h02v09.005.2008237032813'),
                      'mod13a1': (r'^mod13a1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'mod13a1.A2000072.h02v09.005.2008237032813'),
                      'mod13a2': (r'^mod13a2\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'mod13a2.A2000072.h02v09.005.2008237032813'),
                      'mod13a3': (r'^mod13a3\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'mod13a3.A2000072.h02v09.005.2008237032813'),
                      'mod13q1': (r'^mod13q1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'mod13q1.A2000072.h02v09.005.2008237032813'),
                      'myd09a1': (r'^myd09a1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'myd09a1.A2000072.h02v09.005.2008237032813'),
                      'myd09ga': (r'^myd09ga\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'myd09ga.A2000072.h02v09.005.2008237032813'),
                      'myd09gq': (r'^myd09gq\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'myd09gq.A2000072.h02v09.005.2008237032813'),
                      'myd09q1': (r'^myd09q1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'myd09q1.A2000072.h02v09.005.2008237032813'),
                      'myd13a1': (r'^myd13a1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'myd13a1.A2000072.h02v09.005.2008237032813'),
                      'myd13a2': (r'^myd13a2\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'myd13a2.A2000072.h02v09.005.2008237032813'),
                      'myd13a3': (r'^myd13a3\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'myd13a3.A2000072.h02v09.005.2008237032813'),
                      'myd13q1': (r'^myd13q1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                                  'myd13q1.A2000072.h02v09.005.2008237032813')}

        out_schema = {}
        for key in sensor_reg:
            out_schema[key] = {'type': 'object',
                               'properties': {'inputs': {'type': 'array',
                                                         'required': True,
                                                         'items': {'type': 'string',
                                                                   'pattern': sensor_reg[key][0]}},
                                              'products': {'type': 'array',
                                                           'required': True,
                                                           'items': {'type': 'string',
                                                                     'enum': sn.instance(
                                                                         sensor_reg[key][1]).products}}}}

        return out_schema


class Version0Schema(BaseValidationSchema):
    def __init__(self):
        super(Version0Schema, self).__init__()
