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
@requires_auth
def list_orders():
    user = request.authorization.username
    orders = db.list_orders(user)
    return jsonify(orders=orders) 


@app.route('/api/v0/available-products', methods=['GET'])
@requires_auth
def available_products():
    return jsonify(sensor.products)

    
if __name__ == '__main__':
    app.run(host='0.0.0.0')

