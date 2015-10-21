'''
Purpose: module to extract embedded information from product names and supply
configured values for each product
Author: David V. Hill
'''

import re
import logging

logger = logging.getLogger(__name__)


class ProductNotImplemented(NotImplementedError):
    '''Exception to be thrown when trying to instantiate an unsupported
    product'''

    def __init__(self, product_id, *args, **kwargs):
        '''Constructor for the product not implemented

        Keyword args:
        product_id -- The product id of that is not implemented

        Return:
        None
        '''
        self.product_id = product_id
        super(ProductNotImplemented, self).__init__(*args, **kwargs)


class SensorProduct(object):
    '''Base class for all sensor products'''

    # landsat sceneid, modis tile name, aster granule id, etc.
    product_id = None

    # lt5, le7, mod, myd, etc
    sensor_code = None

    # tm, etm, terra, aqua, etc
    sensor_name = None

    # four digits
    year = None

    # three digits
    doy = None

    # last 5 for LANDSAT, collection # for MODIS
    version = None

    # this is a dictionary
    default_pixel_size = {}

    config = {
        'file.extension.landsat.input.filename': '.tar.gz',
        'file.extension.modis.input.filename':'.hdf',
        'pixel.size.dd.09A1': 0.00449155,
        'pixel.size.dd.09GA': 0.00449155,
        'pixel.size.dd.09GQ': 0.002245775,
        'pixel.size.dd.09Q1': 0.002245775,
        'pixel.size.dd.13A1': 0.0089831,
        'pixel.size.dd.13A2': 0.0089831,
        'pixel.size.dd.13A3': 0.0089831,
        'pixel.size.dd.13Q1': 0.002245775,
        'pixel.size.dd.LC8': 0.0002695,
        'pixel.size.dd.LE7': 0.0002695,
        'pixel.size.dd.LO8': 0.0002695,
        'pixel.size.dd.LT4': 0.0002695,
        'pixel.size.dd.LT5': 0.0002695,
        'pixel.size.meters.09A1': 500,
        'pixel.size.meters.09GA': 500,
        'pixel.size.meters.09GQ': 250,
        'pixel.size.meters.09Q1': 250,
        'pixel.size.meters.13A1': 1000,
        'pixel.size.meters.13A2': 1000,
        'pixel.size.meters.13A3': 1000,
        'pixel.size.meters.13Q1': 250,
        'pixel.size.meters.LC8': 30,
        'pixel.size.meters.LE7': 30,
        'pixel.size.meters.LO8': 30,
        'pixel.size.meters.LT4': 30,
        'pixel.size.meters.LT5': 30,
        'sensor.LC8.lta_name': 'LANDSAT_8',
        'sensor.LC8.name': 'olitirs',
        'sensor.LE7.lta_name': 'LANDSAT_ETM_PLUS',
        'sensor.LE7.name': 'etm',
        'sensor.LO8.lta_name': 'LANDSAT_8',
        'sensor.LO8.name': 'oli',
        'sensor.LT4.lta_name': 'LANDSAT_TM',
        'sensor.LT4.name': 'tm',
        'sensor.LT5.lta_name': 'LANDSAT_TM',
        'sensor.LT5.name': 'tm',
        'sensor.MOD.name': 'terra',
        'sensor.MYD.name': 'aqua',
    }
    
 
    def __init__(self, product_id):
        '''Constructor for the SensorProduct base class

        Keyword args:
        product_id -- The product id for the requested product
                      (e.g. Landsat is scene id, Modis is tilename, minus
                      file extension)

        Return:
        None
        '''

        self.product_id = product_id
        self.sensor_code = product_id[0:3]

        __basekey = 'sensor.{0}'.format(self.sensor_code.upper())
        self.sensor_name = self.config.get('{0}.name'.format(__basekey))
        
        try:
            self.lta_name = self.config.get('{0}.lta_name'.format(__basekey))
        except KeyError:
            logger.debug('{0}.lta_name not found in config'.format(__basekey))


class Modis(SensorProduct):
    ''' Superclass for all Modis products '''
    version = None
    short_name = None
    horizontal = None
    vertical = None
    date_acquired = None
    date_produced = None

    def __init__(self, product_id):

        super(Modis, self).__init__(product_id)

        parts = product_id.strip().split('.')

        self.short_name = parts[0]
        self.date_acquired = parts[1][1:]
        self.year = self.date_acquired[0:4]
        self.doy = self.date_acquired[4:8]

        __hv = parts[2]
        self.horizontal = __hv[1:3]
        self.vertical = __hv[4:6]
        self.version = parts[3]
        self.date_produced = parts[4]

        # set the default pixel sizes

        # this comes out to 09A1, 09GA, 13A1, etc
        _product_code = self.short_name.split(self.sensor_code)[1]

        _meters = self.config.get('pixel.size.meters.{0}'.format(_product_code))

        _dd = self.config.get('pixel.size.dd.{0}'.format(_product_code))

        self.default_pixel_size = {'meters': _meters, 'dd': _dd}


class Terra(Modis):
    ''' Superclass for Terra based Modis products '''
    def __init__(self, product_id):
        super(Terra, self).__init__(product_id)


class Aqua(Modis):
    ''' Superclass for Aqua based Modis products '''
    def __init__(self, product_id):
        super(Aqua, self).__init__(product_id)


class ModisTerra09A1(Terra):
    def __init__(self, product_id):
        super(ModisTerra09A1, self).__init__(product_id)


class ModisTerra09GA(Terra):
    def __init__(self, product_id):
        super(ModisTerra09GA, self).__init__(product_id)


class ModisTerra09GQ(Terra):
    def __init__(self, product_id):
        super(ModisTerra09GQ, self).__init__(product_id)


class ModisTerra09Q1(Terra):
    def __init__(self, product_id):
        super(ModisTerra09Q1, self).__init__(product_id)


class ModisTerra13A1(Terra):
    def __init__(self, product_id):
        super(ModisTerra13A1, self).__init__(product_id)


class ModisTerra13A2(Terra):
    def __init__(self, product_id):
        super(ModisTerra13A2, self).__init__(product_id)


class ModisTerra13A3(Terra):
    def __init__(self, product_id):
        super(ModisTerra13A3, self).__init__(product_id)


class ModisTerra13Q1(Terra):
    def __init__(self, product_id):
        super(ModisTerra13Q1, self).__init__(product_id)


class ModisAqua09A1(Aqua):
    def __init__(self, product_id):
        super(ModisAqua09A1, self).__init__(product_id)


class ModisAqua09GA(Aqua):
    def __init__(self, product_id):
        super(ModisAqua09GA, self).__init__(product_id)


class ModisAqua09GQ(Aqua):
    def __init__(self, product_id):
        super(ModisAqua09GQ, self).__init__(product_id)


class ModisAqua09Q1(Aqua):
    def __init__(self, product_id):
        super(ModisAqua09Q1, self).__init__(product_id)


class ModisAqua13A1(Aqua):
    def __init__(self, product_id):
        super(ModisAqua13A1, self).__init__(product_id)


class ModisAqua13A2(Aqua):
    def __init__(self, product_id):
        super(ModisAqua13A2, self).__init__(product_id)


class ModisAqua13A3(Aqua):
    def __init__(self, product_id):
        super(ModisAqua13A3, self).__init__(product_id)


class ModisAqua13Q1(Aqua):
    def __init__(self, product_id):
        super(ModisAqua13Q1, self).__init__(product_id)


class Landsat(SensorProduct):
    ''' Superclass for all landsat based products '''
    path = None
    row = None
    station = None
    lta_product_code = None

    def __init__(self, product_id):

        product_id = product_id.strip()

        super(Landsat, self).__init__(product_id)

        self.path = product_id[3:6].lstrip('0')
        self.row = product_id[6:9].lstrip('0')
        self.year = product_id[9:13]
        self.doy = product_id[13:16]
        self.station = product_id[16:19]
        self.version = product_id[19:21]

        _meters = self.config.get('pixel.size.meters.{0}'
            .format(self.sensor_code.upper()))
        
        _dd = self.config.get('pixel.size.dd.{0}'
            .format(self.sensor_code.upper()))

        self.default_pixel_size = {'meters': _meters, 'dd': _dd}


class LandsatTM(Landsat):
    ''' Models Thematic Mapper based products '''
    def __init__(self, product_id):
        super(LandsatTM, self).__init__(product_id)


class LandsatETM(Landsat):
    ''' Models Enhanced Thematic Mapper Plus based products '''
    def __init__(self, product_id):
        super(LandsatETM, self).__init__(product_id)


class LandsatOLITIRS(Landsat):
    ''' Models combined Landsat 8 OLI/TIRS products '''
    def __init__(self, product_id):
        super(LandsatOLITIRS, self).__init__(product_id)


class LandsatOLI(Landsat):
    ''' Models Landsat 8 OLI only products '''
    def __init__(self, product_id):
        super(LandsatOLI, self).__init__(product_id)


def instance(product_id):
    '''
    Supported MODIS products
    MOD09A1 MOD09GA MOD09GQ MOD09Q1 MYD09A1 MYD09GA MYD09GQ MYD09Q1
    MOD13A1 MOD13A2 MOD13A3 MOD13Q1 MYD13A1 MYD13A2 MYD13A3 MYD13Q1

    MODIS FORMAT:   MOD09GQ.A2000072.h02v09.005.2008237032813

    Supported LANDSAT products
    LT4 LT5 LE7 LC8

    LANDSAT FORMAT: LE72181092013069PFS00
    '''

    # remove known file extensions before comparison
    # do not alter the case of the actual product_id!
    _id = product_id.lower().strip()
    __modis_ext = SensorProduct.config.get('file.extension.modis.input.filename')
    __landsat_ext = SensorProduct.config.get('file.extension.landsat.input.filename')
    
    if _id.endswith(__modis_ext):
        index = _id.index(__modis_ext)
        # leave original case intact
        product_id = product_id[0:index]
        _id = _id[0:index]

    elif _id.endswith(__landsat_ext):
        index = _id.index(__landsat_ext)
        # leave original case intact
        product_id = product_id[0:index]
        _id = _id[0:index]

    instances = {
        'tm': (r'^lt[4|5]\d{3}\d{3}\d{4}\d{3}[a-z]{3}[a-z0-9]{2}$',
               LandsatTM),

        'etm': (r'^le7\d{3}\d{3}\d{4}\d{3}\w{3}.{2}$',
                LandsatETM),

        'olitirs': (r'^lc8\d{3}\d{3}\d{4}\d{3}\w{3}.{2}$',
                    LandsatOLITIRS),

        'oli': (r'^lo8\d{3}\d{3}\d{4}\d{3}\w{3}.{2}$',
                LandsatOLI),

        'mod09a1': (r'^mod09a1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisTerra09A1),

        'mod09ga': (r'^mod09ga\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisTerra09GA),

        'mod09gq': (r'^mod09gq\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisTerra09GQ),

        'mod09q1': (r'^mod09q1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisTerra09Q1),

        'mod13a1': (r'^mod13a1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisTerra13A1),

        'mod13a2': (r'^mod13a2\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisTerra13A2),

        'mod13a3': (r'^mod13a3\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisTerra13A3),

        'mod13q1': (r'^mod13q1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisTerra13Q1),

        'myd09a1': (r'^myd09a1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisAqua09A1),

        'myd09ga': (r'^myd09ga\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisAqua09GA),

        'myd09gq': (r'^myd09gq\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisAqua09GQ),

        'myd09q1': (r'^myd09q1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisAqua09Q1),

        'myd13a1': (r'^myd13a1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisAqua13A1),

        'myd13a2': (r'^myd13a2\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisAqua13A2),

        'myd13a3': (r'^myd13a3\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisAqua13A3),

        'myd13q1': (r'^myd13q1\.a\d{7}\.h\d{2}v\d{2}\.005\.\d{13}$',
                    ModisAqua13Q1)
    }

    for key in instances.iterkeys():
        if re.match(instances[key][0], _id):
            return instances[key][1](product_id.strip())

    msg = "[%s] is not a supported sensor product" % product_id
    raise ProductNotImplemented(product_id, msg)
