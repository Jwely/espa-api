""" Interface for Configuration providers in the espa-api project.  Any
Configuration provider should extend and implement this interface, and any
code that needs configuration should only call methods listed here. Tests
can then be written for the listed methods.  Those two conditions being met
should ensure that unit testing will uncover a broken system before it makes
it into ops """

import abc


class ConfigurationProviderInterfaceV0(object):
    """
    This class should be stateless to allow hot-swapping config variables
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def mode(self):
        """ Returns operational mode [ 'dev' | 'tst' | 'ops' ] """

    @abc.abstractmethod
    def configuration_keys(self):
        """ return list of available configuration keys """

    @abc.abstractmethod
    def url_for(self, service_name):
        """ return the url for the provided service_name """

    @abc.abstractmethod
    def get(self, key):
        """ Retrieves a value for a named key. """

    @abc.abstractmethod
    def put(self, key, value):
        """ Stores a key/value """

    @abc.abstractmethod
    def delete(self, key):
        """ Deletes a key """

    @abc.abstractmethod
    def exists(self, key):
        """ Determines if a key exists in the configuration """

    @abc.abstractmethod
    def load(self, config):
        """ Loads a configuration dump file into the provider """

    @abc.abstractmethod
    def dump(self, path):
        """ Exports current configuration into a dump file """
