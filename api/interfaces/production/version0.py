import traceback
from api.system.logger import ilogger as logger
from api.domain import default_error_message

class API(object):
    def __init__(self, providers=None):
        if providers is not None:
            self.providers = providers()
        else:
            from api.interfaces.providers import DefaultProviders
            self.providers = DefaultProviders()

        self.ordering = self.providers.ordering
        self.inventory = self.providers.inventory
        self.validation = self.providers.validation
        self.metrics = self.providers.metrics
        self.production = self.providers.production
        self.configuration = self.providers.configuration

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

    def update_product_details(self, action, params):
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

    def queue_products(self, order_name_tuple_list, processing_location, job_name):
        """Place products into queued status in bulk

        Args:
            params (dict): {'order_name_list':[], 'processing_loc': '', 'job_name': ''}

        Returns:
            True if successful
        """
        try:
            response = self.production.queue_products(order_name_tuple_list, processing_location, job_name)
        except:
            logger.debug("ERR version0 queue_products"
                         " params: {0}\ntrace: {1}".format((order_name_tuple_list, processing_location, job_name),
                                                           traceback.format_exc()))
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
            if key in self.configuration.configuration_keys:
                response = {key: self.configuration.get(key)}
        except:
            logger.debug("ERR version0 get_production_key, arg: {0}\ntrace: {1}\n".format(key, traceback.format_exc()))
            response = default_error_message

        return response

    def get_production_whitelist(self):
        """
        Returns list of ip addresses in hadoop cluster
        :return: list of strings
        """
        try:
            response = self.production.production_whitelist()
        except:
            logger.debug("ERR failure to generate production whitelist\ntrace: {}".format(traceback.format_exc()))
            response = default_error_message
        return response

    def catch_orphaned_scenes(self):
        """
        Handler for marking queued scenes with no corresponding job in hadoop
        :return: true
        """
        try:
            response = self.production.catch_orphaned_scenes()
        except:
            logger.debug("ERR handling orphaned scenes\ntrace: {}".format(traceback.format_exc()))
            response = default_error_message
        return response

