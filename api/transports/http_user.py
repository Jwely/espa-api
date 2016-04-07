# Contains user facing REST functionality

import flask
from flask import jsonify, make_response, request
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth
from api.interfaces.ordering.version0 import API
from api.domain.user import User
from api.util import lowercase_all
from api.domain import api_operations_v0, default_error_message
from api.system.logger import ilogger as logger
import traceback
import sys
import memcache
from werkzeug.exceptions import BadRequest
import json

espa = API()
auth = HTTPBasicAuth()

cache = memcache.Client(['127.0.0.1:11211'], debug=0)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'msg': 'Invalid username/password'}), 403)


@auth.verify_password

def verify_user(username, password):
    try:
        cache_key = '{}-credentials'.format(username)
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
        cache.set(cache_key, cache_entry, 300)

        user = User(*user_entry)
        flask.g.user = user  # Replace usage with cached version
    except Exception:
        logger.info('Invalid login attempt, username: {}'.format(username))
        return False

    return True


class Index(Resource):
    decorators = [auth.login_required]

    def get(self):
        return 'Welcome to the ESPA API, please direct requests to /api'


class VersionInfo(Resource):
    decorators = [auth.login_required]

    def get(self, version=None):
        info_dict = api_operations_v0['user']

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
    decorators = [auth.login_required]

    def post(self):
        prod_list = request.get_json(force=True)['inputs']
        return espa.available_products(prod_list, auth.username())

    def get(self, prod_id):
        return espa.available_products(prod_id, auth.username())


class ListOrders(Resource):
    decorators = [auth.login_required]

    def get(self, email=None):
        if 'ext' in request.url:
            if email:
                return espa.fetch_user_orders_ext(str(email))
            else:
                return espa.fetch_user_orders_ext(auth.username())
        else:
            if email:
                return espa.fetch_user_orders(str(email))
            else:
                return espa.fetch_user_orders(auth.username())


class ValidationInfo(Resource):
    decorators = [auth.login_required]

    def get(self):
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
    decorators = [auth.login_required]

    def get(self, ordernum):
        if 'order-status' in request.url:
            return espa.order_status(ordernum)
        else:
            return jsonify(espa.fetch_order(ordernum))

    def post(self):
        try:
            user = flask.g.user
            order = request.get_json(force=True)
            print "****** made here 1 "
            if not order:
                message = {"status": 400, "msg": "Unable to parse json data."
                                           "Please ensure your order follows json conventions and your http call is correct."
                                           " If you believe this message is in error please email customer service"}
                print "****** made here 2 "
            else:
                try:
                    print "****** made here 3 "
                    order = lowercase_all(order)
                    orderid = espa.place_order(order, user)
                    if isinstance(orderid, str) and "@" in orderid:
                        print "****** made here 4 "
                        # if order submission was successful, orderid is returned as a string
                        # which includes the submitters email address
                        message = {"status": 200, "orderid": orderid}
                    else:
                        print "****** made here 5 "
                        # there was a problem, and orderid is a dict with the problem details
                        logger.info("problem with user submitted order. user: {0}\n details: {1}".format(user.username, orderid))
                        message = {"status": 400, "message": orderid}
                except Exception as e:
                    logger.debug("exception posting order: {0}\nuser: {1}\n msg: {2}".format(order, user.username, e.message))
                    message = {"status": 500, "msg": "the system experienced an exception. the admins have been notified"}
                    print "****** made here 6 "
        except BadRequest as e:
            # request.get_json throws a BadRequest
            logger.debug("BadRequest, could not parse request into json {}\nuser: {}\nform data {}\n".format(e.description, user.username, request.form))
            message = {"status": 400, "msg": "Could not parse the request into json"}
        except Exception as e:
            logger.debug("ERR posting order. user: {0}\n error: {1}".format(user.username, e))
            message = {"status": 500, "msg": "the system has experienced an exception. the admins have been notified."}

        print "****** made here 7 {}".format(sys.exc_info())
        response = jsonify(message)
        response.status_code = message['status']
        return response


class UserInfo(Resource):
    decorators = [auth.login_required]

    def get(self):
        return flask.g.user.as_dict()


class ItemStatus(Resource):
    decorators = [auth.login_required]

    def get(self, orderid, itemnum='ALL'):
        return espa.item_status(orderid, itemnum)


class Reports(Resource):
    decorators = [auth.login_required]

    def get(self, name=None):
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
    decorators = [auth.login_required]

    def get(self):
        if 'config' in request.url:
            return jsonify(espa.get_system_config())
        else:
            return jsonify(espa.get_system_status())

    def post(self):
        data = request.get_json(force=True)
        try:
            response = espa.update_system_status(data)
            if response == default_error_message:
                message = {'status': 500, 'message': 'internal server error'}
            elif response.keys() == ['msg']:
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
