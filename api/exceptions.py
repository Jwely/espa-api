""" Holds all the custom exceptions raised by the api """

class OrderNotFound(StandardError):
    """Error raised when an order is not found"""

    def __init__(self, orderid):
        """Create new OrderNotFound

        Args:
            orderid (str): The orderid that was not found
        """
        super(OrderNotFound, self).__init__(orderid)


class ItemNotFound(StandardError):
    """Error raised when an item is not found"""

    def __init__(self, orderid, itemid):
        """Create new ItemNotFound

        Args:
            orderid (str): The orderid of the item
            itemid (str): The id of the item that was not found
        """
        super(ItemNotFound, self).__init__(orderid, itemid)
