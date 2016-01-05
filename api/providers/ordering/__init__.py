import abc


class ProviderInterfaceV0(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def place_order(self, username):
        pass

    @abc.abstractmethod
    def list_orders(self, username_or_email):
        pass

    @abc.abstractmethod
    def view_order(self, orderid):
        pass

    @abc.abstractmethod
    def order_status(self, orderid):
        pass

    @abc.abstractmethod
    def item_status(self, orderid, itemid='ALL'):
        pass


class MockOrderingProvider(ProviderInterfaceV0):
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
