from api.providers.inventory import InventoryInterfaceV0

from api import lta, lpdaac
from api.api_exceptions import InventoryException


class InventoryProviderV0(InventoryInterfaceV0):
    def check(self, order):
        LTA_prods = ['tm4', 'tm5', 'etm7', 'olitirs8', 'oli8']
        LPDAAC_prods = ['mod09a1', 'mod09ga', 'mod09gq', 'mod09q1',
                        'myd09a1', 'myd09ga', 'myd09gq', 'myd09q1',
                        'mod13a1', 'mod13a2', 'mod13a3', 'mod13q1',
                        'myd13a1', 'myd13a2', 'myd13a3', 'myd13q1']

        results = {}
        for key in order:
            if key in LTA_prods:
                results = self.check_LTA(order[key]['inputs'])

            elif key in LPDAAC_prods:
                results = self.check_LPDAAC(order[key]['inputs'])

        not_avail = []
        for key, val in results.items():
            if not val:
                not_avail.append(key)

        if not_avail:
            raise InventoryException(not_avail)

    @staticmethod
    def check_LTA(prod_ls):
        return lta.verify_scenes(prod_ls)

    @staticmethod
    def check_LPDAAC(prod_ls):
        return lpdaac.verify_products(prod_ls)


class InventoryProvider(InventoryProviderV0):
    pass


class MockInventoryProvider(InventoryInterfaceV0):
    def check(self, order):
        pass
