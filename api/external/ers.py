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
        self._host = cfg.url_for('ersapi')
        self._secret = cfg.get("ers.%s.secret" % cfg.mode)

    def _api_post(self, url, data):
        # certificate verification fails in dev/tst
        verify = True if cfg.mode == 'ops' else False
        return requests.post(self._host+url, data=data, verify=verify).json()

    def _api_get(self, url, header):
        # certificate verification fails in dev/tst
        verify = True if cfg.mode == 'ops' else False
        return requests.get(self._host+url, headers=header, verify=verify).json()

    def get_user_info(self, user, passw):
        auth_resp = self._api_post('/auth', {'username': user, 'password': passw, 'client_secret': self._secret})
        if not auth_resp['errors']:
            user_resp = self._api_get('/me', {'X-AuthToken': auth_resp['data']['authToken']})
            if not user_resp['errors']:
                return user_resp['data']
            else:
                raise ERSApiException('Error retrieving user {} details. '
                                      'message {}'.format(user, user_resp['errors']))
        else:
            raise ERSApiException('Error authenticating {}. '
                                  'message: {}'.format(user, auth_resp['errors']))
