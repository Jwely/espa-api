import re


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
    """Exceptions when there is an error with validating an order

    example:
    "3 validation errors:": [
      "Value u'' for field '<obj>.tm5.products[0]' cannot be blank'",
      "Value u'' for field '<obj>.tm5.products[0]' is not in the enumeration: ['source_metadata', 'l1', 'toa', 'bt', 'cloud', 'sr', 'lst', 'swe', 'sr_ndvi', 'sr_evi', 'sr_savi', 'sr_msavi', 'sr_ndmi', 'sr_nbr', 'sr_nbr2', 'stats']",
      "Value [u''] for field '<obj>.tm5.products' Requested products are not available"
    ]

    """

    def __init__(self, msg):
        super(ValidationException, self).__init__(msg)

        err_ls = msg.split('\n')
        self.response = {err_ls[0]: []}

        for err in err_ls[1:]:
            if err:
                err = re.sub(r'<obj>.', '', err)
                self.response[err_ls[0]].append(err)


class InventoryException(Exception):
    """Exception for handling problems with inventory handling"""
    def __init__(self, msg):
        super(InventoryException, self).__init__(msg)

        self.response = {'Inputs Not Available': msg}


