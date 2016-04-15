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

        self.admin = self.providers.administration

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

    def update_configuration(self, key=None, value=None, delete=False):
        """
        Provide access to the configuration keys

        :param key: configuration key to match on
        :param value: value to update key to
        :param delete: delete the matching key
        :return: configuration after operation
        """
        try:
            response = self.admin.update_configuration(key=key, value=value, delete=delete)
        except:
            logger.debug('ERR version0 configuration_management:'
                         ' {}\ntrace: {}\n'.format(','.join([key, value, delete]),
                                                   traceback.format_exc()))
            response = default_error_message

        return response

    def load_configuration(self, filepath):
        try:
            response = self.admin.restore_configuration(filepath)
        except:
            logger.debug('ERR version0 load_configuration: '
                         '{}\ntrace: {}\n'.format(filepath, traceback.format_exc()))
            response = default_error_message

        return response

    def backup_configuration(self, filepath=None):
        try:
            response = self.admin.backup_configuration(filepath)
        except:
            logger.debug('ERR version0 backup_configuration: '
                         '{}\ntrace: {}\n'.format(filepath, traceback.format_exc()))

    def order_management(self):
        pass

    def system_management(self):
        pass

    def hadoop_management(self):
        pass

    def onlinecache_management(self):
        pass
