import os
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from flask.ext.login import LoginManager, login_required, current_user
from api.ordering.version0 import API
from api.user import User
from api.domain.config import ApiConfig
from api.utils import lowercase_all
from api.domain import api_operations_v0
from functools import wraps
import base64
import json

api = API()
app = Flask(__name__)
config = ApiConfig()
login_manager = LoginManager()
login_manager.init_app(app)

app.secret_key = config.cfg['key']

# if config.mode == 'dev' or os.environ.get('ESPA_DEBUG'):
#     app.debug = True


@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    api_user = None

    if not token:
        token = request.args.get('token')

    if token:
        token = token.replace('Basic ', '', 1)

        try:
            token = base64.b64decode(token)
        except TypeError:
            pass

        username, password = token.split(":")  # naive token
        user_entry = User.get(username, password)
        if user_entry:
            user = User(*user_entry)
            if user.id:
                api_user = user

    return api_user


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': str(e),
                    'status': 500})


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': str(e),
                    'status': 404})

# request.remote_addr for controlling access by ip address
# for the production-api calls
# remote = request.remote_addr
# if remote not in trusted_proxies:
#     abort(403) #forbidden
def requires_role(cur_user, role):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if role == 'staff' and cur_user.is_staff() is not True:
                return jsonify({'msg': 'access denied'})
            return f(*args, **kwargs)
        return wrapped
    return wrapper


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

    info_dict = api_operations_v0['user']

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


@app.route('/api/v0/order', methods=['POST'])
@login_required
def place_user_order():
    order = {}
    try:
        if request.headers['Content-Type'] == u'application/json':
            order = request.get_json()
        elif request.headers['Content-Type'] == u'application/x-www-form-urlencoded':
            order = json.loads(request.form.keys()[0])
        else:
            order = json.loads(request.data)
    except Exception as e:
        # LOG ME
        pass

    if not order:
        response = {"errmsg": "Unable to parse json data."
                              "Please ensure your order follows json conventions and your http call is correct."
                              " If you believe this message is in error please email customer service"}
    else:
        order = lowercase_all(order)
        response = api.place_order(order, current_user.username)

    return_code = 202 if response.keys()[0] != "errmsg" else 406
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


@app.route('/api/v0/projections', methods=['GET'])
@login_required
def get_projections():
    response = api.validation.fetch_projections()
    return_code = 200 if response.keys()[0] != "errmsg" else 401
    return jsonify(response), return_code


@app.route('/api/v0/formats', methods=['GET'])
@login_required
def get_formats():
    response = api.validation.fetch_formats()
    return_code = 200 if response.keys()[0] != "errmsg" else 401
    return jsonify(response), return_code


@app.route('/api/v0/resampling-methods', methods=['GET'])
@login_required
def get_resampling():
    response = api.validation.fetch_resampling()
    return_code = 200 if response.keys()[0] != "errmsg" else 401
    return jsonify(response), return_code


@app.route('/api/v0/order-schema', methods=['GET'])
@login_required
def get_order_schema():
    response = api.validation.fetch_order_schema()
    return_code = 200 if response.keys()[0] != "errmsg" else 401
    return jsonify(response), return_code

### Production API ###

@app.route('/production-api', methods=['GET'])
#@login_required
#@requires_role(current_user, 'staff')
def get_production_api():
    return jsonify(api.api_versions())

@app.route('/production-api/v0', methods=['GET'])
def get_production_api_ops():
    return jsonify(api_operations_v0['production'])

@app.route('/production-api/v0/products', methods=['GET'])
def get_production_api_products():
    response = api.fetch_production_products(request.args) # request.args is a dict
    return jsonify(response)

@app.route('/production-api/v0/<action>', methods=['POST'])
def update_product(action):
    response = api.update_product_details(action, request.form)
    return jsonify(response)

@app.route('/production-api/v0/handle-orders', methods=['POST'])
def handle_orders():
    response = api.handle_orders()
    return jsonify(response)

@app.route('/production-api/v0/queue-products', methods=['POST'])
def queue_products():
    response = api.queue_products(request.form)
    return jsonify(response)

@app.route('/production-api/v0/configuration/<key>', methods=['GET'])
def get_production_api_config(key):
    response = api.get_production_config(key)
    return jsonify(response)

### End Production ###

if __name__ == '__main__':
    app.run()
    #app.debug = True
    #app.run(host='0.0.0.0', port=5000)



