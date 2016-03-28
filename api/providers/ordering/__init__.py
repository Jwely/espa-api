import abc

class ProviderInterfaceV0(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def sensor_products(product_id):
        """Returns list of all available products for a given scene id"""
        return

    @abc.abstractmethod
    def fetch_user(username):
        """Returns list of user details given a username"""
        return

    @abc.abstractmethod
    def available_products(self, product_id, username):
        """Returns list of products available for a give user"""
        return

    @abc.abstractmethod
    def fetch_user_orders(self, uid):
        """Returns list of orders for a given user"""
        return

    @abc.abstractmethod
    def fetch_order(self, ordernum):
        """Returns details for a given order"""
        return

    @abc.abstractmethod
    def place_order(self, username, order):
        """Method for placing a processing order"""
        return

    @abc.abstractmethod
    def order_status(self, orderid):
        """Return order processing status"""
        return

    @abc.abstractmethod
    def item_status(self, orderid, itemid):
        """Return order item processing status"""
        return


class MockOrderingProvider(object):
    __metaclass__ = abc.ABCMeta

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
