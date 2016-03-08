"""
Purpose: module to extract embedded information from product names and supply
configured values for each product
Author: David V. Hill
"""

import logging

import re
from api.api_exceptions import ProductNotImplemented

logger = logging.getLogger(__name__)


class SensorProduct(object):
    """Base class for all sensor products"""

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

    default_pixel_size = {}

    def __init__(self, product_id):
        """Constructor for the SensorProduct base class

        Keyword args:
        product_id -- The product id for the requested product
                      (e.g. Landsat is scene id, Modis is tilename, minus
                      file extension)

        Return:
        None
        """

        self.product_id = product_id
        self.sensor_code = product_id[0:3]


class Modis(SensorProduct):
    """Superclass for all Modis products"""
    short_name = None
    horizontal = None
    vertical = None
    date_acquired = None
    date_produced = None
    input_filename_extension = '.hdf'
    l1_provider = 'lpdaac'

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


class Terra(Modis):
    """Superclass for Terra based Modis products"""

    sensor_name = 'terra'
    products = ['l1', 'stats']


class Aqua(Modis):
    """Superclass for Aqua based Modis products"""
    products = ['l1', 'stats']
    sensor_name = 'aqua'


class Modis09A1(Modis):
    """models modis 09A1"""
    default_pixel_size = {'meters': 500, 'dd': 0.00449155}


class Modis09GA(Modis):
    """models modis 09GA"""
    default_pixel_size = {'meters': 500, 'dd': 0.00449155}


class Modis09GQ(Modis):
    """models modis 09GQ"""
    default_pixel_size = {'meters': 250, 'dd': 0.002245775}


class Modis09Q1(Modis):
    """models modis 09Q1"""
    default_pixel_size = {'meters': 250, 'dd': 0.002245775}


class Modis13A1(Modis):
    """models modis 13A1"""
    default_pixel_size = {'meters': 1000, 'dd': 0.0089831}


class Modis13A2(Modis):
    """models modis 13A2"""
    default_pixel_size = {'meters': 1000, 'dd': 0.0089831}


class Modis13A3(Modis):
    """models modis 13A3"""
    default_pixel_size = {'meters': 1000, 'dd': 0.0089831}


class Modis13Q1(Modis):
    """models modis 13Q1"""
    default_pixel_size = {'meters': 250, 'dd': 0.002245775}


class ModisTerra09A1(Terra, Modis09A1):
    """models modis 09A1 from Terra"""
    pass


class ModisTerra09GA(Terra, Modis09GA):
    """models modis 09GA from Terra"""
    pass


class ModisTerra09GQ(Terra, Modis09GQ):
    """models modis 09GQ from Terra"""
    pass


class ModisTerra09Q1(Terra, Modis09Q1):
    """models modis 09Q1 from Terra"""
    pass


class ModisTerra13A1(Terra, Modis13A1):
    """models modis 13A1 from Terra"""
    pass


class ModisTerra13A2(Terra, Modis13A2):
    """models modis 13A2 from Terra"""
    pass


class ModisTerra13A3(Terra, Modis13A3):
    """models modis 13A3 from Terra"""
    pass


class ModisTerra13Q1(Terra, Modis13Q1):
    """models modis 13Q1 from Terra"""
    pass


class ModisAqua09A1(Aqua, Modis09A1):
    """models modis 09A1 from Aqua"""
    pass


class ModisAqua09GA(Aqua, Modis09GA):
    """models modis 09GA from Aqua"""
    pass


class ModisAqua09GQ(Aqua, Modis09GQ):
    """models modis 09GQ from Aqua"""
    pass


class ModisAqua09Q1(Aqua, Modis09Q1):
    """models modis 09Q1 from Aqua"""
    pass


class ModisAqua13A1(Aqua, Modis13A1):
    """models modis 13A1 from Aqua"""
    pass


class ModisAqua13A2(Aqua, Modis13A2):
    """models modis 13A2 from Aqua"""
    pass


class ModisAqua13A3(Aqua, Modis13A3):
    """models modis 13A3 from Aqua"""
    pass


class ModisAqua13Q1(Aqua, Modis13Q1):
    """models modis 13Q1 from Aqua"""
    pass


class Landsat(SensorProduct):
    """Superclass for all landsat based products"""
    path = None
    row = None
    station = None
    lta_product_code = None
    default_pixel_size = {'meters': 30, 'dd': 0.0002695}
    input_filename_extension = '.tar.gz'
    l1_provider = 'lta'

    def __init__(self, product_id):
        product_id = product_id.strip()
        super(Landsat, self).__init__(product_id)

        self.path = product_id[3:6].lstrip('0')
        self.row = product_id[6:9].lstrip('0')
        self.year = product_id[9:13]
        self.doy = product_id[13:16]
        self.station = product_id[16:19]
        self.version = product_id[19:21]


class LandsatTM(Landsat):
    """Models Landsat TM only products"""
    products = ["source_metadata", "l1", "toa", "bt", "cloud", "sr", "lst", "swe",
                "sr_ndvi", "sr_evi", "sr_savi", "sr_msavi", "sr_ndmi", "sr_nbr",
                "sr_nbr2", "stats"]
    lta_name = 'LANDSAT_TM'
    sensor_name = 'tm'

    def __init__(self, product_id):
        super(LandsatTM, self).__init__(product_id)


class LandsatETM(Landsat):
    """Models Landsat ETM only products"""
    products = ["source_metadata", "l1", "toa", "bt", "cloud", "sr", "lst", "swe",
                "sr_ndvi", "sr_evi", "sr_savi", "sr_msavi", "sr_ndmi", "sr_nbr",
                "sr_nbr2", "stats"]
    lta_name = 'LANDSAT_ETM_PLUS'
    sensor_name = 'etm'

    def __init__(self, product_id):
        super(LandsatETM, self).__init__(product_id)


class LandsatOLITIRS(Landsat):
    """Models Landsat OLI/TIRS only products"""
    products = ["source_metadata", "l1", "toa", "bt", "cloud", "sr", "sr_ndvi", "sr_evi ",
                "sr_savi", "sr_msavi", "sr_ndmi", "sr_nbr", "sr_nbr2", "stats"]
    lta_name = 'LANDSAT_OLITIRS'
    sensor_name = 'olitirs'

    def __init__(self, product_id):
        super(LandsatOLITIRS, self).__init__(product_id)


class LandsatOLI(Landsat):
    """Models Landsat OLI only products"""
    products = ["source_metadata", "l1", "toa", "cloud", "stats"]
    lta_name = 'LANDSAT_OLI'
    sensor_name = 'oli'

    def __init__(self, product_id):
        super(LandsatOLI, self).__init__(product_id)


class LandsatTIRS(Landsat):
    """Models Landsat TIRS only products"""
    lta_name = 'LANDSAT_TIRS'
    sensor_name = 'tirs'

    def __init__(self, product_id):
        super(LandsatTIRS, self).__init__(product_id)


class Landsat4(Landsat):
    """Models Landsat 4 only products"""

    def __init__(self, product_id):
        super(Landsat4, self).__init__(product_id)


class Landsat4TM(LandsatTM, Landsat4):
    """Models Landsat 4 TM only products"""
    sensor_name = 'tm4'

    def __init__(self, product_id):
        super(Landsat4TM, self).__init__(product_id)
        Landsat4TM.products = [i for i in self.products if i != 'lst']


class Landsat5(Landsat):
    """Models Landsat 5 only products"""

    def __init__(self, product_id):
        super(Landsat5, self).__init__(product_id)


class Landsat5TM(LandsatTM, Landsat5):
    """Models Landsat 5 TM only products"""
    sensor_name = 'tm5'

    def __init__(self, product_id):
        super(Landsat5TM, self).__init__(product_id)


class Landsat7(Landsat):
    """Models Landsat 7 only products"""

    def __init__(self, product_id):
        super(Landsat7, self).__init__(product_id)


class Landsat7ETM(LandsatETM, Landsat7):
    """Models Landsat 7 ETM only products"""
    sensor_name = 'etm7'

    def __init__(self, product_id):
        super(Landsat7ETM, self).__init__(product_id)


class Landsat8(Landsat):
    """Models Landsat 8 only products"""

    def __init__(self, product_id):
        super(Landsat8, self).__init__(product_id)


class Landsat8OLI(LandsatOLI, Landsat8):
    """Models Landsat 8 OLI only products"""
    sensor_name = 'oli8'

    def __init__(self, product_id):
        super(Landsat8OLI, self).__init__(product_id)


class Landsat8TIRS(LandsatTIRS, Landsat8):
    """Models Landsat 8 TIRS only products"""
    sensor_name = 'tirs8'

    def __init__(self, product_id):
        super(Landsat8TIRS, self).__init__(product_id)


class Landsat8OLITIRS(LandsatOLITIRS, Landsat8):
    """Models Landsat 8 OLI/TIRS only products"""
    sensor_name = 'olitirs8'

    def __init__(self, product_id):
        super(Landsat8OLITIRS, self).__init__(product_id)


class SensorCONST(object):
    instances = {
        'tm4': (r'^lt4\d{3}\d{3}\d{4}\d{3}[a-z]{3}[a-z0-9]{2}$',
                Landsat4TM),

        'tm5': (r'^lt5\d{3}\d{3}\d{4}\d{3}[a-z]{3}[a-z0-9]{2}$',
                Landsat5TM),

        'etm7': (r'^le7\d{3}\d{3}\d{4}\d{3}\w{3}.{2}$',
                 Landsat7ETM),

        'olitirs8': (r'^lc8\d{3}\d{3}\d{4}\d{3}\w{3}.{2}$',
                     Landsat8OLITIRS),

        'oli8': (r'^lo8\d{3}\d{3}\d{4}\d{3}\w{3}.{2}$',
                 Landsat8OLI),

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

    LTA_ids = ['tm4', 'tm5', 'etm7', 'olitirs8', 'oli8']
    LPDAAC_ids = ['mod09a1', 'mod09ga', 'mod09gq', 'mod09q1',
                    'myd09a1', 'myd09ga', 'myd09gq', 'myd09q1',
                    'mod13a1', 'mod13a2', 'mod13a3', 'mod13q1',
                    'myd13a1', 'myd13a2', 'myd13a3', 'myd13q1']

    def __setattr__(self, key, value):
        pass


def instance(product_id):
    """
    Supported MODIS products
    MOD09A1 MOD09GA MOD09GQ MOD09Q1 MYD09A1 MYD09GA MYD09GQ MYD09Q1
    MOD13A1 MOD13A2 MOD13A3 MOD13Q1 MYD13A1 MYD13A2 MYD13A3 MYD13Q1

    MODIS FORMAT:   MOD09GQ.A2000072.h02v09.005.2008237032813

    Supported LANDSAT products
    LT4 LT5 LE7 LC8 LO8

    LANDSAT FORMAT: LE72181092013069PFS00
    """

    # remove known file extensions before comparison
    # do not alter the case of the actual product_id!
    _id = product_id.lower().strip()
    __modis_ext = Modis.input_filename_extension
    __landsat_ext = Landsat.input_filename_extension

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

    instances = SensorCONST.instances

    for key in instances.iterkeys():
        if re.match(instances[key][0], _id):
            inst = instances[key][1](product_id.strip())
            inst.shortname = key
            return inst

    msg = u"[{0:s}] is not a supported sensor product".format(product_id)
    raise ProductNotImplemented(msg)


def available_products(input_products):
    """Lists all the available products for each input_product

    Args:
        input_products (iterable): An iterable of input_product names (str)

    Returns:
        dict: { 'tm5': {'outputs': [output, products],
                       'inputs': [supplied, input, products]},
                'etm7': ... }

    Raises:
        ProductNotImplemented if an unknown product is supplied
    """
    if not hasattr(input_products, '__iter__'):
        raise TypeError('input_products must be iterable')

    result = {}

    for product in input_products:
        try:
            inst = instance(product)
            name = inst.shortname
            if name not in result:
                result[name] = {'outputs': inst.products,
                                'inputs': [product]}
            else:
                result[name]['inputs'].append(product)
        except ProductNotImplemented:
            if 'not_implemented' not in result:
                result['not_implemented'] = [product]
            else:
                result['not_implemented'].append(product)
    return result
