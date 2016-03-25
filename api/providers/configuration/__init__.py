''' Interface for Configuration providers in the espa-api project.  Any
Configuration provider should extend and implement this interface, and any
code that needs configuration should only call methods listed here. Tests
can then be written for the listed methods.  Those two conditions being met
should ensure that unit testing will uncover a broken system before it makes
it into ops '''

import abc

class ConfigurationProviderInterfaceV0(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        '''
        Keyword args:
        use_cache - Whether to check the cache provider for
        extras - The dictionary to add the retry_after value to

        Returns:
        A dictionary with retry_after populated with the datetimestamp after
        which an operation should be retried.
        '''
        return

    @abc.abstractmethod
    def mode(self):
        ''' Returns operational mode [ 'dev' | 'tst' | 'ops' ] '''
        return

    @abc.abstractmethod
    def configuration_keys(self):
        ''' return list of available configuration keys '''
        return

    @abc.abstractmethod
    def url_for(self, service_name):
        ''' return the url for the provided service_name '''
        return

    @abc.abstractmethod
    def get(self, key):
        ''' Retrieves a value for a named key. '''
        return

    @abc.abstractmethod
    def put(self, key, value):
        ''' Stores a key/value '''
        return

    @abc.abstractmethod
    def mget(self, keys):
        ''' Retrieves multiple values for an iterable of keys '''
        return

    @abc.abstractmethod
    def mput(self, kv_dict):
        ''' Stores a dictionary of key values '''
        return

    @abc.abstractmethod
    def mdelete(self, keys):
        ''' Deletes multiple values for an iterable of keys '''
        return

    @abc.abstractmethod
    def exists(self, key):
        ''' Determines if a key exists in the configuration '''
        return

# Public interface methods.  May be called directly
def load(self, config):
    '''' Loads a configuration dump file into the provider '''
    return

def dump(self, path):
    ''' Exports current configuration into a dump file '''
    return
