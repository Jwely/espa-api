import abc


class AdministrationProviderException(Exception):
    pass


class AdminProviderInterfaceV0(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def access_configuration(self, key=None, value=None, delete=False):
        """
        View or update a configuration key
        Defaults to listing all configuration keys & values

        :param key: configuration key to look for
        :param value: new value for the key
        :param delete: remove key from configuration
        """

    @abc.abstractmethod
    # def restore_configuration(self, filepath, clear=False):
    def restore_configuration(self, filepath):
        """
        Update the configuration table from a file

        :param filepath: path to sql file
        :param clear: truncate the configuration table first
        """

    @abc.abstractmethod
    def backup_configuration(self, path=None):
        """
        Create a backup of the current configuration table

        :param path: path of the sql file to create
        :return: Bool
        """

    @abc.abstractmethod
    def jobs(self, jobid=None, stop=False):
        """
        View current hadoop jobs or kill the job
        Defaults to listing all the jobs

        :param jobid: specific job to look at
        :param stop: stop the specified job
        """

    @abc.abstractmethod
    def system(self, key=None, disposition='on'):
        """
        System related operation to switch on/off

        :param disposition: 'on' or 'off'
        :param key: system or subsystem to toggle
        """

    @abc.abstractmethod
    def onlinecache(self, list_orders=False, orderid=None, filename=None,
                    delete=False):
        """
        Operations related to dealing with the LUSTRE cache

        :param delete: delete specified orderid/filename
        :param list_orders: list current order on the disk
        :param orderid: list specific order on the disk
        :param filename: filename for a specified order
        """

    @abc.abstractmethod
    def orders(self, query=None, cancel=False):
        """
        Provide access to orders
        Defaults to displaying information for all orders in the system

        :param query: Used to return specific order(s)
        :param cancel: cancel a specific orderid
        """
    @abc.abstractmethod
    def products(self, query=None, resubmit=None):
        """
        Provide access to products in the system
        Defaults to displaying information for all products in the system

        :param query: list products that meet the specified criteria
        :param resubmit: resubmits supplied products
        """
