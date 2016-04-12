''' Holds logic necessary for interacting with the online distribution
cache '''

import re
import os

from api.util import sshcmd
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.system.logger import ilogger as logger

config = ConfigurationProvider()

class OnlineCacheException(Exception):
    """ General exception raised from the OnlineCache """
    pass

class OnlineCache(object):
    """ Client code to interact with the LSRD online cache """

    __default_order_path = '/data2/science_lsrd/LSRD/orders'
    __order_path_key = 'online_cache_orders_dir'

    def __init__(self, host=None, user=None, pw=None):

        if host is None:
            host = config.get('landsatds.host')
        if user is None:
            user = config.get('landsatds.username')
        if pw is None:
            pw = config.get('landsatds.password')

        self.client = sshcmd.RemoteHost(host, user, pw, debug=False)

        try:
            self.orderpath = config.get(self.__order_path_key)
        except:
            logger.info('{0} not defined in configurations, setting objects orderpath to {1}'
                .format(self.__order_path_key, self.__default_order_path))

            self.orderpath = self.__default_order_path

    def delete(self, orderid, filename=None):
        """ Removes an order from physical online cache disk """

        self.check_orderid(orderid)

        if filename:
            path = os.path.join(self.orderpath, orderid, filename)
        else:
            path = os.path.join(self.orderpath, orderid)

        # this should be the dir where the order is held
        logger.info('Deleting {0} from online cache'.format(path))

        self.execute_command('sudo chattr -fR -i {0};rm -rf {0}'.format(path))

    def list(self, orderid=None):
        if orderid:
            self.check_orderid(orderid)

        if orderid:
            path = os.path.join(self.orderpath, orderid)
        else:
            path = self.orderpath

        cmd = 'ls {}'.format(path)

        result = self.execute_command(cmd)
        ret = tuple(x.rstrip() for x in result['stdout'])

        return ret

    def check_orderid(self, orderid):
        espa_order = r'[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}-[0-9]{6,8}-[0-9]{3,6}'
        ee_order = r'[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}-[0-9]{13}'

        if not (re.match(espa_order, orderid) or re.match(ee_order, orderid)):
            raise OnlineCacheException('invalid orderid parameter specified:{0}'.format(orderid))

    def capacity(self):
        """ Returns the capacity of the online cache """

        cmd = 'df -mhP {0}'.format(self.orderpath)

        result = self.execute_command(cmd)

        line = result['stdout'][1].split(' ')

        clean = [l for l in line if len(l) > 0]

        results = {'capacity': clean[1],
                   'used': clean[2],
                   'available': clean[3],
                   'percent_free': clean[4]}

        return results

    def execute_command(self, cmd):
        try:
            result = self.client.execute(cmd)
        except Exception, exception:
            raise OnlineCacheException(exception)

        if result['stderr'] is not None and len(result['stderr']) > 0:
            raise OnlineCacheException('Error executing command: {}'
                                       'stderr returned: {}'
                                       .format(cmd, result['stderr']))

        logger.debug('call to {0} returned {1}'.format(cmd, result['stdout']))


        return result

# Below here should be considered to be the public interface for this module

def delete(orderid):
    return OnlineCache().delete(orderid)

def capacity():
    return OnlineCache().capacity()
