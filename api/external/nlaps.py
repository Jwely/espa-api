'''
Purpose: Simple lookup to determine if a Landsat 5 scene is TMA or not
Author: David V. Hill
'''

import os
from api.system.logger import api_logger as logger

class NLAPS(object):

    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.path = os.path.join(self.path, 'tma_scenes.txt')

        with open(self.path, 'rb') as nl:
            data = nl.read()
            self.keys = {k.strip():True for k in data.split('\n')}
            data = None


def products_are_nlaps(product_list):

    if not isinstance(product_list, list):
        raise TypeError("product_list must be an instance of list()")

    results = []

    nl = NLAPS()

    for p in product_list:
        if p in nl.keys:
            results.append(p)
    return results
