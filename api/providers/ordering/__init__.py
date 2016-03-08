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
    def staff_products(product_id):
        """Returns list of products available to staff"""
        return

    @abc.abstractmethod
    def pub_products(product_id):
        """Returns list of products available to the public"""
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


class ProductionProviderInterfaceV0(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def queue_products(order_name_tuple_list, processing_location, job_name):
        ''' Allows the caller to place products into queued status in bulk '''
        return

    @abc.abstractmethod
    def mark_product_complete(self, name=None, orderid=None, processing_loc=None,
                                completed_file_location=None, destination_cksum_file=None,
                                log_file_contents=None):
        ''' Marks product complete in the local and in EE system if applicable '''
        return

    @abc.abstractmethod
    def set_product_unavailable(self, name=None, orderid=None,
                                processing_loc=None, error=None, note=None):
        ''' Marks product unavailable locally and in EE system if applicable  '''
        return

    @abc.abstractmethod
    def set_products_unavailable(products, reason):
        '''Bulk updates products to unavailable status and updates EE if
        necessary.
        Keyword args:
        products - A list of models.Scene objects
        reason - The user facing reason the product was rejected
        '''
        return

    @abc.abstractmethod
    def update_status(self, name=None, orderid=None,
                        processing_loc=None, status=None):
        ''' update a scene's status '''
        return

    @abc.abstractmethod
    def update_product(self, action, name=None, orderid=None, processing_loc=None,
                        status=None, error=None, note=None,
                        completed_file_location=None,
                        cksum_file_location=None,
                        log_file_contents=None):
        ''' wrapper method for update_status, set_product_error,
        set_product_unavailable, mark_product_complete '''
        return

    @abc.abstractmethod
    def set_product_retry(self, name, orderid, processing_loc,
                        error, note, retry_after, retry_limit=None):
        ''' Set a product to retry status '''
        return

    @abc.abstractmethod
    def set_product_error(self, name=None, orderid=None,
                            processing_loc=None, error=None):
        ''' handle product error  '''
        return

    @abc.abstractmethod
    def get_products_to_process(self, record_limit=500,
                                for_user=None,
                                priority=None,
                                product_types=['landsat', 'modis'],
                                encode_urls=False):
        '''Find scenes that are oncache and return them as properly formatted
        json per the interface description between the web and processing tier'''
        return

    @abc.abstractmethod
    def load_ee_orders():
        ''' Loads all the available orders from lta into
        our database and updates their status
        '''
        return

    @abc.abstractmethod
    def handle_retry_products(self):
        ''' handles all products in retry status '''
        return

    @abc.abstractmethod
    def handle_onorder_landsat_products(self):
        ''' handles landsat products still on order '''
        return

    @abc.abstractmethod
    def send_initial_emails(self):
        ''' sends initial emails '''
        return

    @abc.abstractmethod
    def handle_submitted_landsat_products(self):
        ''' handles all submitted landsat products '''
        return

    @abc.abstractmethod
    def handle_submitted_modis_products(self):
        ''' Moves all submitted modis products to oncache if true '''
        return


    @abc.abstractmethod
    def handle_submitted_plot_products(self):
        ''' Moves plot products from submitted to oncache status once all
            their underlying rasters are complete or unavailable '''
        return

    @abc.abstractmethod
    def handle_submitted_products(self):
        ''' handles all submitted products in the system '''
        return

    @abc.abstractmethod
    def send_completion_email(order):
        ''' public interface to send the completion email '''
        return

    @abc.abstractmethod
    def update_order_if_complete(order):
        '''Method to send out the order completion email
        for orders if the completion of a scene
        completes the order

        Keyword args:
        orderid -- id of the order

        '''
        return

    @abc.abstractmethod
    def finalize_orders(self):
        '''Checks all open orders in the system and marks them complete if all
        required scene processing is done'''
        return

    @abc.abstractmethod
    def purge_orders(send_email=False):
        ''' Will move any orders older than X days to purged status and will also
        remove the files from disk'''
        return

    @abc.abstractmethod
    def handle_orders(self):
        '''Logic handler for how we accept orders + products into the system'''
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
