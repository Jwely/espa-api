from api.providers.inventory import InventoryInterfaceV0

from api import lta, lpdaac
from api.api_exceptions import InventoryException
from api.domain import sensor


class InventoryProviderV0(InventoryInterfaceV0):
    """
    Check incoming orders against supported inventories
    """
    def check(self, order):
        LTA_prods = sensor.SensorCONST.LTA_prods
        LPDAAC_prods = sensor.SensorCONST.LPDAAC_prods

        lta_ls = []
        lpdaac_ls = []
        results = {}
        for key in order:
            if key in LTA_prods:
                lta_ls.extend(order[key]['inputs'])
            elif key in LPDAAC_prods:
                lpdaac_ls.extend(order[key]['inputs'])

        if lta_ls:
            results.update(self.check_LTA(lta_ls))
        if lpdaac_ls:
            results.update(self.check_LPDAAC(lpdaac_ls))

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
