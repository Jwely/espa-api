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


class ProductNotImplemented(NotImplementedError):
    """Exception to be thrown when trying to instantiate an unsupported
    product"""

    def __init__(self, product_id):
        """Constructor for the product not implemented

        Keyword args:
        product_id -- The product id of that is not implemented

        Return:
        None
        """
        self.product_id = product_id
        super(ProductNotImplemented, self).__init__(product_id)


class ValidationException(Exception):
    """Exception when there is an error with validating an order"""
    pass
