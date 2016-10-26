# Contains user facing REST functionality

import flask
import memcache

from api.interfaces.ordering.version1 import API as APIv1
from api.domain import user_api_operations
from api.system.logger import ilogger as logger
from api.util import api_cfg
from api.util import lowercase_all
from api.domain.user import User

from flask import jsonify
from flask import make_response
from flask import request
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Resource

from werkzeug.exceptions import BadRequest

from functools import wraps

espa = APIv1()
auth = HTTPBasicAuth()
cache = memcache.Client(['127.0.0.1:11211'], debug=0)


def greylist(func):
    """
    Provide a decorator to enact black and white lists on user endpoints

    References http://flask.pocoo.org/docs/0.11/deploying/wsgi-standalone/#proxy_setups
    and http://github.com/mattupsate/flask-security
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        black_ls = api_cfg().get('user_blacklist')
        white_ls = api_cfg().get('user_whitelist')
        denied_response = make_response(jsonify({'msg': 'Access Denied'}), 403)

        if 'X-Forwarded-For' in request.headers:
            remote_addr = request.headers.getlist('X-Forwarded-For')[0].rpartition(' ')[-1]
        else:
            remote_addr = request.remote_addr or 'untrackable'

        # prohibited ip's
        if black_ls:
            if remote_addr in black_ls.split(','):
                return denied_response

        # for when were guarding access
        if white_ls:
            if remote_addr not in white_ls.split(','):
                return denied_response

        return func(*args, **kwargs)
    return decorated


def version_filter(func):
    """
    Provide a decorator to enact a version filter on all endpoints
    """
    def decorated(*args, **kwargs):
        versions = user_api_operations.keys()
        url_version = request.url.split('/')[4].replace('v', '')
        if url_version in versions:
            return func(*args, **kwargs)
        else:
            msg = 'Invalid API version %s' % url_version
            return make_response(jsonify({'msg', msg}), 404)
    return decorated


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'msg': 'Invalid username/password'}), 403)


@auth.verify_password
def verify_user(username, password):
    try:
        # usernames with spaces are valid in EE, though they can't be used for cache keys
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


class Index(Resource):
    decorators = [greylist]

    @staticmethod
    def get():
        return 'Welcome to the ESPA API, please direct requests to /api'


class VersionInfo(Resource):
    decorators = [auth.login_required, greylist]

    def get(self, version=None):
        info_dict = user_api_operations

        if version:
            if version in info_dict:
                response = info_dict[version]
                return_code = 200
            else:
                ver_str = ", ".join(info_dict.keys())
                err_msg = "%s is not a valid api version, these are: %s" % (version, ver_str)
                response = {"errmsg": err_msg}
                return_code = 404
        else:
            response = espa.api_versions()
            return_code = 200

        return response, return_code


class AvailableProducts(Resource):
    decorators = [auth.login_required, greylist, version_filter]

    @staticmethod
    def post(version):
        prod_list = request.get_json(force=True)['inputs']
        return espa.available_products(prod_list, auth.username())

    @staticmethod
    def get(version, prod_id):
        return espa.available_products(prod_id, auth.username())


class ListOrders(Resource):
    decorators = [auth.login_required, greylist, version_filter]

    @staticmethod
    def get(version, email=None):
        try:
            filters = request.get_json(force=True)
        except:
            # no json this time
            filters = {}

        if 'ext' in request.url:
            if email:
                return espa.fetch_user_orders_ext(str(email), filters)
            else:
                return espa.fetch_user_orders_ext(auth.username(), filters)
        elif 'feed' in request.url:
            return espa.fetch_user_orders_feed(email)
        else:
            if email:
                return espa.fetch_user_orders(str(email))
            else:
                return espa.fetch_user_orders(auth.username())


class ValidationInfo(Resource):
    decorators = [auth.login_required, greylist, version_filter]

    @staticmethod
    def get(version):
        param = request.url
        response = None

        if 'projections' in param:
            response = espa.validation.fetch_projections()
        elif 'formats' in param:
            response = espa.validation.fetch_formats()
        elif 'resampling-methods' in param:
            response = espa.validation.fetch_resampling()
        elif 'order-schema' in param:
            response = espa.validation.fetch_order_schema()

        return response


class Ordering(Resource):
    decorators = [auth.login_required, greylist, version_filter]

    @staticmethod
    def get(version, ordernum):
        if 'order-status' in request.url:
            return espa.order_status(ordernum)
        else:
            return jsonify(espa.fetch_order(ordernum))

    @staticmethod
    def post(version):
        try:
            user = flask.g.user
            order = request.get_json(force=True)
            if not order:
                message = {"status": 400, "msg": "Unable to parse json data. Please ensure your order follows json "
                                                 "conventions and your http call is correct. If you believe this "
                                                 "message is in error please email customer service"}
            else:
                try:
                    order = lowercase_all(order)
                    orderid = espa.place_order(order, user)
                    if isinstance(orderid, str) and "@" in orderid:
                        # if order submission was successful, orderid is returned as a string
                        # which includes the submitters email address
                        message = {"status": 200, "orderid": orderid}
                    else:
                        # there was a problem, and orderid is a dict with the problem details
                        logger.info("problem with user submitted order. user: {0}\n details: {1}".format(user.username, orderid))
                        message = {"status": 400, "message": orderid}
                except Exception as e:
                    logger.debug("exception posting order: {0}\nuser: {1}\n msg: {2}".format(order, user.username, e.message))
                    message = {"status": 500, "msg": "the system experienced an exception. the admins have been notified"}
        except BadRequest as e:
            # request.get_json throws a BadRequest
            logger.debug("BadRequest, could not parse request into json {}\nuser: {}\nform data {}\n".format(e.description, user.username, request.form))
            message = {"status": 400, "msg": "Could not parse the request into json"}
        except Exception as e:
            logger.debug("ERR posting order. user: {0}\n error: {1}".format(user.username, e))
            message = {"status": 500, "msg": "the system has experienced an exception. the admins have been notified."}

        response = jsonify(message)
        response.status_code = message['status']
        return response


class UserInfo(Resource):
    decorators = [auth.login_required, greylist, version_filter]

    @staticmethod
    def get(version):
        return flask.g.user.as_dict()


class ItemStatus(Resource):
    decorators = [auth.login_required, greylist, version_filter]

    @staticmethod
    def get(version, orderid, itemnum='ALL'):
        user = flask.g.user
        return espa.item_status(orderid, itemnum, user.username)
