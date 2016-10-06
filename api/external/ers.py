'''
Purpose: ERS API client module
Author: Clay Austin
'''

import requests
from api.providers.configuration.configuration_provider import ConfigurationProvider

cfg = ConfigurationProvider()


class ERSApiException(Exception):
    pass


class ERSApi(object):

    def __init__(self):
        self._host = 'https://ers.cr.usgs.gov/api'
        self._secret = cfg.get("ers.%s.secret" % cfg.mode)
        # till we know devsys and devmast hosts
        self._secret = cfg.get("ers.ops.secret")

    def _api_post(self, url, data):
        return requests.post(self._host+url, data=data)

    def _api_get(self, url, header):
        return requests.get(self._host+url, headers=header)

    def get_user_info(self, username, password):
        data = {'username': username,
                'password': password,
                'client_secret': self._secret}
        auth_resp = self._api_post('/auth', data).json()
        if not auth_resp['errors']:
            token = auth_resp['data']['authToken']
            header = {'X-AuthToken': token}
            user_resp = self._api_get('/me', header).json()
            return user_resp
        else:
            raise ERSApiException('Error authenticating {}. message: {}'.format(username, auth_resp['errors']))
