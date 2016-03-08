''' Holds logic necessary for interacting with the online distribution
cache '''

import re
from api.util import sshcmd
from api.system.config import ApiConfig
from api.system.logger import api_logger as logger

config = ApiConfig()

class OnlineCacheException(Exception):
    ''' General exception raised from the OnlineCache '''
    pass

class OnlineCache(object):
    ''' Client code to interact with the LSRD online cache '''

    __default_order_path = '/data2/science_lsrd/LSRD/orders'
    __order_path_key = 'online_cache_orders_dir'

    def __init__(self, host=None, user=None, pw=None):

        if host is None:
            host = config.settings['landsatds.host']
        if user is None:
            user = config.settings['landsatds.username']
        if pw is None:
            pw = config.settings['landsatds.password']

        self.client = sshcmd.RemoteHost(host, user, pw, debug=False)

        try:
            self.orderpath = config.settings[self.__order_path_key]
        except:
            logger.info('{0} not defined in configurations, setting objects orderpath to {1}'
                .format(self.__order_path_key, self.__default_order_path))
            # don't see why this needs to happen
            #config = Configuration()
            #config.key = self.__order_path_key
            #config.value = self.__default_order_path
            #config.save()

            self.orderpath = self.__default_order_path

    def delete(self, orderid):
        ''' Removes an order from physical online cache disk '''

        # centrally locate this in the settings and pull in here plus urls.py
        espa_order = r'[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}-[0-9]{6,8}-[0-9]{3,6}'
        ee_order = r'[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}-[0-9]{13}'

        if not (re.match(espa_order, orderid) or re.match(ee_order, orderid)):
            raise OnlineCacheException('invalid orderid parameter specified:{0}'.format(orderid))

        path = '/'.join([self.orderpath, orderid])

        # this should be the dir where the order is held
        logger.info('Deleting {0} from online cache'.format(path))

        try:
            result = self.client.execute('sudo chattr -fR -i {0};rm -rf {0}'.format(path))
        except Exception, exception:
            raise OnlineCacheException(exception)

        if result['stderr'] is not None and len(result['stderr']) > 0:
            raise OnlineCacheException('Error deleting order {0}: {1}'
                .format(orderid, result['stderr']))

    def capacity(self):
        ''' Returns the capacity of the online cache '''

        cmd = 'df -mhP {0}'.format(self.orderpath)
        try:
            result = self.client.execute(cmd)
        except Exception, exception:
            raise OnlineCacheException(exception)

        if result['stderr'] is not None and len(result['stderr']) > 0:
            raise OnlineCacheException('Error retrieving cache capacity:{0}'
                .format(result['stderr']))

        logger.debug('call to {0} returned {1}'.format(cmd, result['stdout']))

        line = result['stdout'][1].split(' ')

        clean = [l for l in line if len(l) > 0]

        results = {'capacity':clean[1],
                   'used':clean[2],
                   'available':clean[3],
                   'percent_free':clean[4]}
        return results

# Below here should be considered to be the public interface for this module

def delete(orderid):
    return OnlineCache().delete(orderid)

def capacity():
    return OnlineCache().capacity()
