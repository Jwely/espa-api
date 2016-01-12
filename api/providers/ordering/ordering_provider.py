from api.domain import sensor

class OrderingProvider(object):
    def available_products(self, product_id):
        prod_list = product_id.split(",")
        return sensor.available_products(prod_list)

    def fetch_user_orders(self, user_id):
        # does user exist in system
        # what orders does user have in system
        # if user does not exist, return dict with 
        # key of 'errmsg'
        pass




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
