import time
import psycopg2
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from flask.ext.login import LoginManager, UserMixin, login_required, current_user

from api.ordering.version0 import API
from api import lta

from api.dbconnect import DBConnect
from api.utils import get_cfg
from api.utils import is_empty

app = Flask(__name__)
app.debug = True
login_manager = LoginManager()
login_manager.init_app(app)

api = API()

class User(UserMixin):
    cfg = get_cfg()['config']
    cfg['cursor_factory'] = psycopg2.extras.DictCursor

    def __init__(self, username, email, first_name, last_name):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

        # check if user exists in our DB, if
        # not create them, and assign self.id
        self.id = User.find_or_create_user(self.username, self.email, self.first_name, self.last_name)

    @classmethod
    def get(cls,username,password):
        user_tup = None
        try:
            lta_user = lta.get_user_info(username, password)
            user_tup = (str(username), str(lta_user.email), str(lta_user.first_name), str(lta_user.last_name))
        except Exception as e:
            raise e.message
            #logger.exception('Exception retrieving user[{0}] from earth '
            #                 'explorer during login'.format(username))

        return user_tup

    @classmethod
    def find_or_create_user(cls, username, email, first_name, last_name):
        user_id = None
        nownow = time.strftime('%Y-%m-%d %H:%M:%S')
        insert_stmt = "insert into auth_user (username, " \
                      "email, first_name, last_name, password, " \
                      "is_staff, is_active, is_superuser, " \
                      "last_login, date_joined) values {};"
        arg_tup = (username, email, first_name, last_name,
                    'pass', 'f', 't', 'f', nownow, nownow)

        with DBConnect(**cls.cfg) as db:
            user_sql = "select id from auth_user where username = %s;"
            db.select(user_sql, username)
            if is_empty(db):
                # we need to create a local user
                db.execute(insert_stmt.format(arg_tup))
                db.commit()
            # user should be there now, lets try this again
            db.select(user_sql, username)
            user_id = db[0][0]

        return user_id


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


if __name__ == '__main__':
    app.run()
    #app.debug = True
    #app.run(host='0.0.0.0', port=5000)



