''' Holds logic necessary for interacting with the online distribution
cache '''

import re
import os

from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.util import sshcmd
from api.system.logger import ilogger as logger


class OnlineCacheException(Exception):
    """ General exception raised from the OnlineCache """
    pass


class OnlineCache(object):
    """ Client code to interact with the LSRD online cache """

    config = ConfigurationProvider()

    __order_path_key = 'online_cache_orders_dir'
    __host_key = 'landsatds.host'
    __user_key = 'landsatds.username'
    __pw_key = 'landsatds.password'

    def __init__(self):
        self.orderpath = self.config.get(self.__order_path_key)

        if not self.orderpath:
            msg = '{} not defined in configurations'.format(self.__order_path_key)
            logger.debug(msg)
            raise OnlineCacheException(msg)

        host, user, pw = self.config.get([self.__host_key,
                                          self.__user_key,
                                          self.__pw_key])

        self.client = sshcmd.RemoteHost(host, user, pw, timeout=5)

        try:
            self.client.execute('ls')
        except Exception as e:
            logger.debug('No connection to OnlineCache host: {}'.format(e))
            raise OnlineCacheException(e)

    def delete(self, orderid, filename=None):
        """
        Removes an order from physical online cache disk

        :param filename: file to delete inside of an order
        :param orderid: associated order to delete
        """
        if filename:
            path = os.path.join(self.orderpath, orderid, filename)
        else:
            path = os.path.join(self.orderpath, orderid)

        # this should be the dir where the order is held
        logger.info('Deleting {} from online cache'.format(path))

        self.execute_command('sudo chattr -fR -i {0};rm -rf {0}'.format(path))

        return True

    def list(self, orderid=None):
        """
        List the orders currently stored on cache, or files listed
        insed of a specific order

        :param orderid: order name to look inside of
        :return: list of folders/files
        """
        if orderid:
            path = os.path.join(self.orderpath, orderid)
        else:
            path = self.orderpath

        cmd = 'ls {}'.format(path)

        result = self.execute_command(cmd)
        ret = tuple(x.rstrip() for x in result['stdout'])

        return ret

    def check_orderid(self, orderid):
        """
        Verify the format of the order id given

        :param orderid: name to check
        :return: True if the id passes, otherwise raise an exception
        """
        espa_order = r'[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}-[0-9]{6,8}-[0-9]{3,6}'
        ee_order = r'[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}-[0-9]{13}'

        if not (re.match(espa_order, orderid) or re.match(ee_order, orderid)):
            raise OnlineCacheException('Invalid Order ID specified')

        return True

    def capacity(self):
        """
        Returns the capacity of the online cache

        :return: dict
        """

        cmd = 'df -mhP {}'.format(self.orderpath)

        result = self.execute_command(cmd)

        line = result['stdout'][1].split(' ')

        clean = [l for l in line if len(l) > 0]

        results = {'capacity': clean[1],
                   'used': clean[2],
                   'available': clean[3],
                   'percent_free': clean[4]}

        return results

    def execute_command(self, cmd):
        """
        Execute the given command on the cache

        :param cmd: cmd string to execute
        :return: results of the command
        """
        try:
            result = self.client.execute(cmd)
        except Exception, exception:
            logger.debug('Error executing command: {} '
                         'Raised exception: {}'.format(cmd, exception))
            raise OnlineCacheException(exception)

        if 'stderr' in result and result['stderr']:
            logger.debug('Error executing command: {} '
                         'stderror returned: {}'.format(cmd, result['stderr']))

            raise OnlineCacheException(result['stderr'])

        logger.info('call to {} returned {}'.format(cmd, result))

        return result


def delete(orderid):
    return OnlineCache().delete(orderid)


def capacity():
    return OnlineCache().capacity()
