"""API interface for placing and viewing orders.

   Any methods exposed through this interface are intended to be consumed by
   end users (publicly). The module should be the pure interface for the api
   functions.  Don't import or include any implementation specific items here,
   just logic.  Implementations are touched through the registry.
"""
import traceback
from api.system.logger import api_logger as logger
from api.domain import default_error_message
from api.system.config import ApiConfig
from api import ValidationException, InventoryException


class API(object):
    def __init__(self, providers=None):
        if providers is not None:
            self.providers = providers()
        else:
            from api.interfaces.ordering.providers import DefaultProviders
            self.providers = DefaultProviders()

        self.ordering = self.providers.ordering
        self.inventory = self.providers.inventory
        self.validation = self.providers.validation
        self.metrics = self.providers.metrics
        self.production = self.providers.production

    def api_versions(self):
        """
        Provides list of available api versions

        Returns:
            dict: of api versions and a description

        Example:
            {
                "0":
                    "description": "Demo access points for development",
                }
            }
        """
        return self.providers.api_versions

    def available_products(self, product_id, username):
        """
        Provides list of available products given
        a scene id.

        Args:
            product_id (str): the scene id to retrieve list of availabe products for.

        Returns:
            dict: of available products

        Example:
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
        try:
            response = self.ordering.available_products(product_id, username)
        except:
            logger.debug("ERR version0 available_prods_get product_id: {0} "
                         "username: {1}\nexception {2}".format(product_id, username,
                                                               traceback.format_exc()))
            response = default_error_message

        return response

    def fetch_user_orders(self, user_id):
        """ Return orders given a user id

        Args:
            user_id (str): The email or username for the user who placed the order.

        Returns:
            dict: of orders with list of order ids
        """
        try:
            response = self.ordering.fetch_user_orders(user_id)
        except:
            logger.debug("ERR version0 fetch_user_orders arg: {0}\nexception {1}".format(user_id, traceback.format_exc()))
            response = default_error_message

        return response

    def fetch_order(self, ordernum):
        """ Returns details of a submitted order

        Args:
            ordernum (str): the order id of a submitted order

        Returns:
            dict: of order details
        """
        try:
            response = self.ordering.fetch_order(ordernum)
        except:
            logger.debug("ERR version0 fetch_order arg: {0}\nexception {1}".format(ordernum, traceback.format_exc()))
            response = default_error_message

        return response

    def place_order(self, order, user):
        """Enters a new order into the system.

        Args:
            :keyword order (api.domain.order.Order): The order to be entered into the system

        Returns:
            str: The generated order id

        Raises:
            api.api_exceptions.ValidationException: Error occurred validating params
            api.api_exceptions.InventoryException: Items were not found/unavailable
        """
        try:
            # perform validation, raises ValidationException
            order = self.validation.validate(order, user.username)
            # performs inventory check, raises InventoryException
            self.inventory.check(order)
            # track metrics
            self.metrics.collect(order)
            # capture the order
            response = self.ordering.place_order(order, user)
        except ValidationException as e:
            logger.info('Invalid order received: {0}\nresponse {1}'.format(order, e.response))
            # Need to format the string repr of the exception for end user consumption
            response = e.response
        except InventoryException as e:
            logger.info('Requested inputs not available: {0}\nresponse {1}'.format(order, e.response))
            response = e.response
        except:
            logger.debug("ERR version0 place_order arg: {0}\nexception {1}".format(order, traceback.format_exc()))
            response = default_error_message

        return response

    def order_status(self, orderid):
        """Shows an order status

        Orders contain additional information such as date ordered, date completed,
        current status and so on.

        Args:
            orderid (str): id of the order

        Raises:
            OrderNotFound if the order did not exist
        """
        try:
            response = self.ordering.order_status(orderid)
        except:
            logger.debug("ERR version0 order_status arg: {0}\nexception {1}".format(orderid, traceback.format_exc()))
            response = default_error_message

        return response

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
        try:
            response = self.ordering.item_status(orderid, itemid)
        except:
            logger.debug("ERR version0 item_status itemid {0}  orderid: {1}\nexception {2}".format(itemid, orderid, traceback.format_exc()))
            response = default_error_message

        return response

    ####################
    ####################
    ## Production API ##
    ####################
    ####################

    def fetch_production_products(self, params):
        """Returns products ready for production

        Arg:
            params (dict): with the following keys:
                        for_user (str): username on the order
                        priority (str): 'high' | 'normal' | 'low'
                        product_types (str): 'modis,landsat'
                        encode_urls (bool): True | False

        Returns:
            list: list of products
        """
        try:
            response = self.production.get_products_to_process(**params)
        except:
            logger.debug("ERR version0 fetch_production_products, params: {0}\ntrace: {1}\n".format(params, traceback.format_exc()))
            response = default_error_message

        return response

    def update_product_details(self, action, params=None):
        """Update product details

        Args:
            action (str): name of the action to peform. valid values include:
                            update_status, set_product_error,
                            set_product_unavailable,
                            mark_product_complete
            params (dict): args for the action. valid keys: name, orderid,
                            processing_loc, status, error, note,
                            completed_file_location, cksum_file_location,
                            log_file_contents

        Returns:
            True if successful
        """
        try:
            response = self.production.update_product(action, **params)
        except:
            logger.debug("ERR version0 update_product_details, params: {0}\ntrace: {1}\n".format(params, traceback.format_exc()))
            response = default_error_message

        return response

    def handle_orders(self):
        """Handler for accepting orders and products into the processing system

        Args:
            none

        Returns:
            True if successful
        """
        try:
            response = self.production.handle_orders()
        except:
            logger.debug("ERR version0 handle_orders. trace: {0}".format(traceback.format_exc()))
            response = default_error_message

        return response

    def queue_products(self, params):
        """Place products into queued status in bulk

        Args:
            params (dict): {'order_name_list':[], 'processing_loc': '', 'job_name': ''}

        Returns:
            True if successful
        """
        try:
            response = self.production.queue_products(*params)
        except:
            logger.debug("ERR version0 queue_products params: {0}\ntrace: {1}".format(params, traceback.format_exc()))
            response = default_error_message

        return response

    def get_production_key(self, key):
        """Returns value for given configuration key

        Arg:
            str representation of key

        Returns:
            dict: of key and value
        """
        try:
            response = {"msg": "'{0}' is not a valid key".format(key)}
            if key in ApiConfig().settings.keys():
                response = {key: ApiConfig().settings[key]}
        except:
            logger.debug("ERR version0 get_production_key, arg: {0}\ntrace: {1}\n".format(key, traceback.format_exc()))
            response = default_error_message

        return response

