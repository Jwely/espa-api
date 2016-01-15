"""API interface for placing and viewing orders.

   Any methods exposed through this interface are intended to be consumed by
   end users (publicly). The module should be the pure interface for the api
   functions.  Don't import or include any implementation specific items here,
   just logic.  Implementations are touched through the registry.
"""


class API(object):
    def __init__(self, providers=None):
        if providers is not None:
            self.providers = providers()
        else:
            from api.ordering.providers import DefaultProviders
            self.providers = DefaultProviders()

        self.ordering = self.providers.ordering
        self.inventory = self.providers.inventory
        self.validation = self.providers.validation
        self.metrics = self.providers.metrics

    def api_versions(self):
        """
        Provides list of available api versions
        Returns: dictionary
            {
                "0": 
                    "description": "Demo access points for development",
                }
            }
        """
        return self.providers.api_versions

    def available_products(self, product_id):
        """
        Provides list of available products given
        a scene id.

        Args:
            keyword: product_id - the scene id to retrieve list of availabe products for.

        Returns: dictionary
            {
              "etm": {
                  "inputs": [
                        "LE70290302003123EDC00"
                            ],
                            "outputs": [
                                "etm_sr",
                                "etm_toa",
                                "etm_l1",
                                "source",
                                "source_metadata"
                              ]
                            },
                            "not_implemented": [
                              "bad scene id"
                            ],
                    }
        """
        return self.ordering.available_products(product_id)

    def fetch_user_orders(self, user_id):
        """ Return orders given a user id

        Args:
            :keyword user_id  : The email or username for the user who placed the order.

        Returns:
            dict: {'orders': [list of orderids]}
        """
        return self.ordering.fetch_user_orders(user_id)

    def fetch_order(self, ordernum):
        """Retrieves a submitted order
        Args:
            ordernum
        Returns:
            dict
        """
        return self.ordering.fetch_order(ordernum)

    def place_order(self, order):
        """Enters a new order into the system.

        Args:
            :keyword order (api.domain.order.Order): The order to be entered into the system

        Returns:
            str: The generated order id

        Raises:
            api.exceptions.ValidationException: Error occurred validating params
            api.exceptions.InventoryException: Items were not found/unavailable
        """
        # perform validation, raises ValidationException
        self.validation(order)

        # performs inventory check, raises InventoryException
        self.inventory.check(order)

        # track metrics
        self.metrics.collect(order)

        # capture the order
        return self.ordering.place_order(order)

    def list_orders(self, username_or_email):
        """Returns all the orders for the user

        Args:
            username_or_email (str): Username or email address of user

        Returns:
            list: A list of all the users orders (order ids).  May be zero length
        """
        return self.ordering.list_orders(username_or_email)

    def view_order(self, orderid):
        """Show details for a user order

        Args:
            orderid (str): The orderid to view

        Returns:
            api.domain.order.Order: Same information as when placing the order

        Raises:
            OrderNotFound:
        """
        return self.ordering.view_order(orderid)

    def order_status(self, orderid):
        """Shows an order status

        Orders contain additional information such as date ordered, date completed,
        current status and so on.

        Args:
            orderid (str): id of the order

        Raises:
            OrderNotFound if the order did not exist
        """
        return self.ordering.order_status(orderid)

    def item_status(self, orderid, itemid='ALL'):
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
        return self.ordering.item_status(orderid, itemid)
