"""API interface for placing and viewing orders.

   Any methods exposed through this interface are intended to be consumed by
   end users (publicly). The module should be the pure interface for the api
   functions.  Don't import or include any implementation specific items here,
   just logic.  Implementations are touched through the registry.
"""

from api.ordering import registry


def place_order(order):

    """Enters a new order into the system.

    Args:
        Order (api.domain.order.Order): The order to be entered into the system
        
    Returns:
        str: The generated order id

    Raises:
        api.exceptions.ValidationException: Error occurred validating params
        api.exceptions.InventoryException: Items were not found/unavailable
    """
    # perform validation, raises ValidationException
    registry.validation.validate(order)

    # performs inventory check, raises InventoryException
    registry.inventory.check(order)

    # track metrics
    registry.metrics.collect(order)

    # capture the order
    return registry.ordering.place_order(order)


def list_orders(username_or_email):
    """Returns all the orders for the user

    Args:
        username_or_email (str): Username or email address of user

    Returns:
        list: A list of all the users orders (order ids).  May be zero length
    """
    return registry.ordering.list_orders(username_or_email)


def view_order(orderid):
    """Show details for a user order

    Args:
        orderid (str): The orderid to view

    Returns:
        api.domain.order.Order: Same information as when placing the order

    Raises:
        OrderNotFound:
    """
    return registry.ordering.view_order(orderid)


def order_status(orderid):
    """Shows an order status

    Orders contain additional information such as date ordered, date completed,
    current status and so on.

    Args:
        orderid (str): id of the order

    Raises:
        OrderNotFound if the order did not exist
    """
    return registry.ordering.order_status(orderid)


def item_status(orderid, itemid='ALL'):
    """Shows an individual item status

    Args:
        orderid (str): id of the order
        itemid (str): id of the item.  If ALL is specified, a list of status
                      for all items in the order will be returned.

    Returns:
        list: list of dictionaries with status, completion_time and note

    Raises:
        ItemNotFound if the item did not exist
    """
    return registry.ordering.item_status(orderid, itemid)
