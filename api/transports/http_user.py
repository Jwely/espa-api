# Contains user facing REST functionality

import flask
from flask import Flask, jsonify, abort, make_response, request
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth

from api.interfaces.ordering.version0 import API
from api.domain.user import User
from api.system.config import ApiConfig
from api.util import lowercase_all
from api.domain import api_operations_v0


espa = API()
auth = HTTPBasicAuth()


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'msg': 'Invalid username/password'}), 403)


@auth.verify_password
def verify_user(username, password):
    # api_user = None

    try:
        user_entry = User.get(username, password)
        user = User(*user_entry)
        flask.g.user = user
        # if user.id:
        #     api_user = user
    except Exception as e:
        print e
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

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('product_ids', type=list,
                                   required=True, help='Usage: {"inputs": ["list", "of", "inputs"]}',
                                   location='json')
        super(AvailableProducts, self).__init__()

    def post(self):
        prod_list = request.get_json(force=True)['inputs']
        return espa.available_products(prod_list, auth.username())

    def get(self, prod_id):
        return espa.available_products(prod_id, auth.username())


class ListOrders(Resource):
    decorators = [auth.login_required]

    def get(self, email=None):
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
        order = {}
        try:
            order = request.get_json(force=True)
        except Exception as e:
            # LOG ME
            pass

        if not order:
            response = {"errmsg": "Unable to parse json data."
                        "Please ensure your order follows json conventions and your http call is correct."
                        " If you believe this message is in error please email customer service"}

        else:
            order = lowercase_all(order)
            response = espa.place_order(order, flask.g.get('user'))

        return response

class UserInfo(Resource):
    decorators = [auth.login_required]

    def get(self):
        return flask.g.user.as_dict()

class ItemStatus(Resource):
    decorators = [auth.login_required]

    def get(self, orderid, itemnum='ALL'):
        return espa.item_status(orderid, itemnum)
