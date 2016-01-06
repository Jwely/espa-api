from api.domain import sensor

class OrderingProvider(object):
    def available_products(self, product_id):
        return sensor.available_products([product_id])

    def place_order(self, username):
        pass

    def list_orders(self, username_or_email):
        pass

    def view_order(self, orderid):
        pass

    def order_status(self, orderid):
        pass

    def item_status(self, orderid, itemid='ALL'):
        """

        :rtype: str
        """
        pass
