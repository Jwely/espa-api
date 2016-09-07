# Contains Admin facing REST functionality

import flask
import memcache
import traceback

from api.domain import default_error_message, admin_api_operations

from api.interfaces.admin.version1 import API as APIv1
from api.system.logger import ilogger as logger
from api.domain.user import User

from flask import jsonify
from flask import make_response
from flask import request
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Resource


espa = APIv1()
auth = HTTPBasicAuth()
cache = memcache.Client(['127.0.0.1:11211'], debug=0)


def whitelist(func):
    """
    Provide a decorator to enact a white filter on an endpoint

    References http://flask.pocoo.org/docs/0.11/deploying/wsgi-standalone/#proxy_setups
    and http://github.com/mattupsate/flask-security
    """
    def decorated(*args, **kwargs):
        white_ls = espa.get_admin_whitelist()
        if 'X-Forwarded-For' in request.headers:
            remote_addr = request.headers.getlist('X-Forwarded-For')[0].rpartition(' ')[-1]
        else:
            remote_addr = request.remote_addr or 'untrackable'

        if remote_addr in white_ls:
            return func(*args, **kwargs)
        else:
            return make_response(jsonify({'msg': 'Access Denied'}), 403)
    return decorated


def version_filter(func):
    """
    Provide a decorator to enact a version filter on all endpoints
    """
    def decorated(*args, **kwargs):
        versions = admin_api_operations.keys()
        url_version = request.url.split('/')[4].replace('v','')
        if url_version in versions:
            return func(*args, **kwargs)
        else:
            msg = 'Invalid API version %s' % url_version
            return make_response(jsonify({'msg': msg}), 404)
    return decorated


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'msg': 'Invalid username/password'}), 403)


@auth.verify_password
def verify_user(username, password):
    try:
        cache_key = '{}-credentials'.format(username.replace(' ', '_espa_cred_insert_'))
        cache_entry = cache.get(cache_key)

        if cache_entry:
            # Need to be encrypted?
            if cache_entry['password'] == password:
                user_entry = cache_entry['user_entry']

            # User may have changed their password while it was still cached
            else:
                user_entry = User.get(username, password)
        else:
            user_entry = User.get(username, password)

        cache_entry = {'password': password,
                       'user_entry': user_entry}
        cache.set(cache_key, cache_entry, 7200)

        user = User(*user_entry)
        flask.g.user = user  # Replace usage with cached version
    except Exception:
        logger.info('Invalid login attempt, username: {}'.format(username))
        return False

    return True


class Reports(Resource):
    decorators = [auth.login_required, whitelist, version_filter]

    @staticmethod
    def get(version, name=None):
        if 'report' in request.url:
            if name:
                return espa.get_report(name)
            else:
                return espa.available_reports()
        else:
            # statistics
            if name:
                return espa.get_stat(name)
            else:
                return espa.available_stats()


class SystemStatus(Resource):
    decorators = [auth.login_required, whitelist, version_filter]

    @staticmethod
    def get(version):
        if 'config' in request.url:
            return jsonify(espa.get_system_config())
        else:
            return jsonify(espa.get_system_status())

    @staticmethod
    def post(version):
        data = request.get_json(force=True)
        try:
            response = espa.update_system_status(data)
            if response == default_error_message:
                message = {'status': 500, 'message': 'internal server error'}
            elif isinstance(response, dict) and response.keys() == ['msg']:
                message = {'status': 400, 'message': response['msg']}
            else:
                message = {'status': 200, 'message': 'success'}

            resp = jsonify(message)
            resp.status_code = message['status']
            return resp
        except:
            logger.debug("ERROR updating system status: {0}".format(traceback.format_exc()))
            message = {'status': 500, 'message': 'internal server error'}
            resp = jsonify(message)
            resp.status_code = 500
            return resp


class OrderResets(Resource):
    decorators = [auth.login_required, whitelist, version_filter]

    @staticmethod
    def put(version, orderid):
        # eg 'error_to_unavailable'
        _to_whole = request.url.split('/')[-2]
        # eg 'unavailable'
        _to_state = _to_whole.split('_')[-1]
        return espa.error_to(orderid, _to_state)

