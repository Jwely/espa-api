'''
Purpose: Simple lookup to determine if a Landsat 5 scene is TMA or not
Author: David V. Hill
'''

import os


class NLAPS(object):
    """
    Simple class to hold TMA scene id's
    """
    path = os.path.join(os.path.dirname(__file__), 'tma_scenes.txt')

    with open(path, 'r') as f:
        keys = set(s.strip() for s in f)


def products_are_nlaps(product_list):
    """
    Compare the requested products with products that cannot be processed

    Changed to use set for performance
    :param product_list: requested products
    :return: products that cannot be processed
    """

    if not isinstance(product_list, list):
        raise TypeError("product_list must be an instance of list()")

    nl = NLAPS
    matches = nl.keys.intersection(set(product_list))

    return list(matches)
