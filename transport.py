import os
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from flask.ext.login import LoginManager, login_required, current_user
from api.ordering.version0 import API
from api.user import User
from api.domain.config import ApiConfig

api = API()
app = Flask(__name__)
config = ApiConfig()
login_manager = LoginManager()
login_manager.init_app(app)

if config.mode == 'dev' or os.environ.get('ESPA_DEBUG'):
    app.debug = True

@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    api_user = None
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username,password = token.split(":") # naive token
        user_entry = User.get(username,password)
        if (user_entry is not None):
            # user has successfully authenticated with EE
            # lets find or create them on our side
            user = User(user_entry[0],user_entry[1],user_entry[2],user_entry[3])
            if user.id:
                api_user = user

    return api_user

@app.route('/')
def index():
    return 'Welcome to the ESPA API, please direct requests to /api'

@app.route('/api')
@login_required
def api_versions():
  return jsonify(api.api_versions())

@app.route('/api/v<version>')
@login_required
def api_info(version):
    info_dict = {
        '0': {
            'description': 'Version 0 of the ESPA API',
            'operations': {
                "/api": {
                    'function': "list versions",
                    'methods': [
                        "HEAD",
                        "GET"
                    ]
                },
                "/api/v0": {
                    'function': "list operations",
                    'methods': [
                        "HEAD",
                        "GET"
                    ]
                },
                "/api/v0/available-products/<product_ids>": {
                    'function': "list available products per sceneid",
                    'comments': "comma separated ids supported",
                    'methods': [
                        "HEAD",
                        "GET"
                    ]
                },
                "/api/v0/available-products": {
                    'function': "list available products per sceneid",
                    'comments': 'sceneids should be delivered in the product_ids parameter, comma separated if more than one',
                    'methods': [
                        "HEAD",
                        "POST"
                    ]
                },
                "/api/v0/projections": {
                    'function': "list available projections",
                    'methods': [
                        "HEAD",
                        "GET"
                    ]
                },
                "/api/v0/formats": {
                    'function': "list available output formats",
                    'methods': [
                        "HEAD",
                        "GET"
                    ]
                },
                "/api/v0/resampling-methods": {
                    'function': "list available resampling methods",
                    'methods': [
                        "HEAD",
                        "GET"
                    ]
                },
                "/api/v0/orders": {
                    'function': "list orders for authenticated user",
                    'methods': [
                        "HEAD",
                        "GET"
                    ]
                },
                "/api/v0/orders/<email>": {
                    'function': "list orders for supplied email, for user collaboration",
                    'methods': [
                        "HEAD",
                        "GET"
                    ]
                },
                "/api/v0/order/<ordernum>": {
                    'function': "retrieves a submitted order",
                    'methods': [
                        "HEAD",
                        "GET"
                    ]
                },
                "/api/v0/request/<ordernum>": {
                    'function': "retrieve order sent to server",
                    'methods': [
                        "HEAD",
                        "GET"
                    ]
                },
                "/api/v0/order": {
                    'function': "point for accepting processing requests via HTTP POST with JSON body. Errors are returned to user, successful validation returns an orderid",
                    'methods': [
                        "POST"
                    ]
                },
            }
        }
    }

    if info_dict.__contains__(version):
        response = info_dict[version]
    else:
        ver_str = ", ".join(info_dict.keys())
        err_msg = "%s is not a valid api version, these are: %s" % (version, ver_str)
        response = {"errmsg": err_msg}

    return_code = 200 if response.keys()[0] != "errmsg" else 401

    return jsonify(response), return_code

@app.route('/api/v0/available-products/<product_id>', methods=['GET'])
@login_required
def available_prods_get(product_id):
    return jsonify(api.available_products(product_id, current_user.username))

@app.route('/api/v0/available-products', methods=['POST'])
@login_required
def available_prods_post():
    x = request.form['product_ids']
    return jsonify(api.available_products(x, current_user.username))

@app.route('/api/v0/orders', methods=['GET'])
@login_required
def get_user_orders():
    response = api.fetch_user_orders(current_user.username)
    return_code = 200 if response.keys()[0] != "errmsg" else 401
    return jsonify(response), return_code

@app.route('/api/v0/orders/<email>', methods=['GET'])
@login_required
def get_order_by_email(email):
    response = api.fetch_user_orders(str(email))
    return_code = 200 if response.keys()[0] != "errmsg" else 401
    return jsonify(response), return_code

@app.route('/api/v0/order/<ordernum>', methods=['GET'])
@login_required
def get_order_by_ordernum(ordernum):
    response = api.fetch_order(ordernum)
    return jsonify(response)

@app.route('/api/v0/order-status/<ordernum>', methods=['GET'])
@login_required
def get_order_status_by_ordernum(ordernum):
    response = api.order_status(ordernum)
    return jsonify(response)

@app.route('/api/v0/item-status/<orderid>', methods=['GET'])
@app.route('/api/v0/item-status/<orderid>/<itemnum>', methods=['GET'])
@login_required
def get_item_status(orderid, itemnum='ALL'):
    response = api.item_status(orderid, itemnum)
    return jsonify(response)

@app.route('/api/v0/user', methods=['GET'])
@login_required
def get_current_user():
    response = current_user.as_dict()
    return jsonify(response)

if __name__ == '__main__':
    app.run()
    #app.debug = True
    #app.run(host='0.0.0.0', port=5000)



