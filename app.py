import flask
from flask import Flask
from flask import Response
from flask import request
from flask import g
from flask import url_for
from flask import abort
from flask import jsonify

from functools import wraps

from storage import Storage
from configuration import Configuration
import sensor
import schema

DEBUG = True
SECRET_KEY = 'not a secret'


app = Flask(__name__)
app.config.from_object(__name__)

db = Storage()
config = Configuration()

def login_required():
    return Response('Not authenticated',
                    401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    '''If you are using basic auth with mod_wsgi you will have to enable auth forwarding,
      otherwise apache consumes the required headers and does 
      not send it to your application: WSGIPassAuthorization.'''
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not db.login(auth.username, auth.password):
            return login_required()
        return f(*args, **kwargs)
    return decorated


@app.route('/api', methods=['GET'])
def list_versions():
    resp = {
        'version_0': {
            'url': '/api/v0',
            'description': 'Demo URLS for development'
        }        
    }
    return jsonify(resp)


@app.route('/api/v0', methods=['GET'])
def list_operations():
    links = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            links[rule.rule] = {'methods':list(rule.methods),
                                'endpoint': rule.endpoint}
    return jsonify(links)


@app.route('/api/v0/authenticate', methods=['POST'])
def authenticate():
    body = request.get_json(force=True)

    result = db.login(body['username'],
                      body['password'])
    return jsonify({"result":result})
   

@app.route('/api/v0/user', methods=['GET'])
@requires_auth
def user_info():
    user = request.authorization.username
    app.logger.debug('User info for {0}'.format(user))
    info = db.user_info(user)
    return jsonify({'first_name':info['first_name'],
                    'last_name': info['last_name'],
                    'email': info['email'],
                    'username': user,
                    'roles': info['roles']})


@app.route('/api/v0/orders', methods=['GET'])
@app.route('/api/v0/orders/<email>', methods=['GET'])
@requires_auth
def list_orders(email=None):
    orders = None
    if email is None:
        user = request.authorization.username
    else:
        try:
            user = db.username(email)
            orders = db.list_orders(user)
        except:
            pass
    return jsonify(orders=orders)


@app.route('/api/v0/order', methods=['POST'])
@requires_auth
def place_order():
    user = request.authorization.username
    order = request.get_json(force=True)
    v = schema.OrderValidator(schema.order_schema)
    if v.validate(order) == False:
        return jsonify(errors=v.errors)
    else:
        return jsonify(db.save_order(user, order))


@app.route('/api/v0/order/<ordernum>', methods=['GET'])
@requires_auth
def order_details(ordernum):
    return jsonify(db.view_order(ordernum))


@app.route('/api/v0/available-products', methods=['POST'])
@app.route('/api/v0/available-products/<product_id>', methods=['GET'])
@requires_auth
def available_products(product_id=None):
    if request.method == 'GET':
        return jsonify(sensor.available_products([product_id]))
    elif request.method == 'POST':
        body = request.get_json(force=True)
        return jsonify(sensor.available_products(body['inputs']))

@app.route('/api/v0/projections', methods=['GET'])
@requires_auth
def projections():
    return jsonify(schema.projections)

@app.route('/api/v0/formats', methods=['GET'])
@requires_auth
def formats():
    return jsonify(formats=schema.formats)

@app.route('/api/v0/resampling-methods', methods=['GET'])
@requires_auth
def resampling_methods():
    return jsonify(resampling_methods=schema.resampling_methods)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

