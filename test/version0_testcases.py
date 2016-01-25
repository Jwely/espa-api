BASE = {'tm5': {'inputs': ['LT50290302002123EDC00'],
                'products': ['sr']},
        'projection': {},
        'image_extents': {},
        'format': 'gtiff',
        'resize': {},
        'resampling_method': 'nn',
        'plot_statistics': False}

formats = ['gtiff', 'hdf-eos2', 'envi']
resampling_methods = ['nn', 'bil', 'cc']


def good_orders():
    sensor_acqids = {'.A2000072.h02v09.005.2008237032813': ['MOD09A1', 'MOD09GA', 'MOD09GQ', 'MOD09Q1',
                                                            'MYD09A1', 'MYD09GA', 'MYD09GQ', 'MYD09Q1',
                                                            'MOD13A1', 'MOD13A2', 'MOD13A3', 'MOD13Q1',
                                                            'MYD13A1', 'MYD13A2', 'MYD13A3', 'MYD13Q1'],
                     '2181092013069PFS00': ['LT4', 'LT5', 'LE7', 'LO8', 'LC8']}
