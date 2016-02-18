'''
Purpose: lpdaac services client module
Author: David V. Hill
'''

import logging
import requests
import os

from ordering.models.configuration import Configuration as config

from ordering import sensor
from ordering import utilities

logger = logging.getLogger(__name__)


class LPDAACService(object):

    def __init__(self):
        self.datapool = config.url_for('modis.datapool')        
        
    def verify_products(self, products):
        response = {}

        if isinstance(products, str):
            products = [products]

        for product in products:

            if isinstance(product, str):
                product = sensor.instance(product)

            response[product.product_id] = self.input_exists(product)

        return response

    def input_exists(self, product):
        '''Determines if a LPDAAC product is available for download

        Keyword args:
        product - The name of the product

        Returns:
        True/False
        '''

        if isinstance(product, str) or isinstance(product, unicode):
            product = sensor.instance(product)

        result = False

        try:
            url = self.get_download_url(product)

            if 'download_url' in url[product.product_id]:

                url = url[product.product_id]['download_url']

                response = None

                try:
                    response = requests.head(url)
                    if response.ok is True:
                        result = True
                except Exception, e:
                    logger.exception('Exception checking modis input {0}\n '
                                     'Exception:{1}'
                                     .format(url, e))
                    return result
                finally:
                    if response is not None:
                        response.close()
                        response = None

        except sensor.ProductNotImplemented:
            logger.warn('{0} is not an implemented LPDAAC product'
                        .format(product))

        return result

    def get_download_url(self, product):

        url = {}

        #be nice and accept a string
        if isinstance(product, str) or isinstance(product, unicode):
            product = sensor.instance(product)

        #also be nice and accept a sensor.Modis object
        if isinstance(product, sensor.Modis):

            path = self._build_modis_input_file_path(product)

            product_url = ''.join([self.datapool, path])

            if not product_url.lower().startswith("http"):
                product_url = ''.join(['http://', product_url])

            if not product.product_id in url:
                url[product.product_id] = {}

            url[product.product_id]['download_url'] = product_url

        return url

    def get_download_urls(self, products):

        urls = {}

        if not isinstance(products, list):
            raise TypeError("get_download_urls requires a list of products")

        for product in products:
            urls.update(self.get_download_url(product))

        return urls


    def _build_modis_input_file_path(self, product):

        if isinstance(product, str) or isinstance(product, unicode):
            product = sensor.instance(product)

        if isinstance(product, sensor.Aqua):
            base_path = config.get('path.aqua_base_source')
        elif isinstance(product, sensor.Terra):
            base_path = config.get('path.terra_base_source')
        else:
            msg = "Cant build input file path for unknown LPDAAC product:%s"
            raise Exception(msg % product.product_id)

        date = utilities.date_from_doy(product.year, product.doy)

        path_date = "%s.%s.%s" % (date.year,
                                  str(date.month).zfill(2),
                                  str(date.day).zfill(2))

        input_extension = config.get('file.extension.modis.input.filename')

        input_file_name = "%s%s" % (product.product_id, input_extension)

        path = os.path.join(base_path,
                            '.'.join([product.short_name.upper(),
                                      product.version.upper()]),
                            path_date.upper(), input_file_name)

        return path


def input_exists(product):
    return LPDAACService().input_exists(product)


def verify_products(products):
    return LPDAACService().verify_products(products)

def get_download_url(product):
    return LPDAACService().get_download_url(product)

def get_download_urls(products):
    return LPDAACService().get_download_urls(products)
