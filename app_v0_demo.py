import flask
from flask import Flask
from flask import Response
from flask import request
from flask import g
from flask import url_for
from flask import abort
from flask import jsonify

from functools import wraps

DEBUG = True
SECRET_KEY = 'not a secret'
USERS = {
    'admin': {'password': 'password',
              'email': 'admin@email.com',
              'first_name': 'Admin',
              'last_name': 'Person',
              'roles': ['admin', 'user', 'production'],
    },
    'user': {'password': 'password',
              'email': 'user@email.com',
              'first_name': 'User',
              'last_name': 'Person',
              'roles': ['user'],
    },
    'production': {'password': 'password',
              'email': 'production@email.com',
              'first_name': 'Production',
              'last_name': 'Person',
              'roles': ['user', 'production'],
    }    
}

 
ORDERS = {
    'production': {
        'processing@email.com-101015143201-00132': {
            'status': 'ordered',
            'order_source': 'bulk api',
            'priority': 'high',
            'order_date': '2015-10-10',
            'completion_date': '',
            'note': '',
            'ee_order_id': '',
            'order_type': 'ondemand',
            'initial_email_sent': '2015-10-10',
            'completion_email_sent': '',
            'inputs': {
                'LT50290302002123EDC00': {
                    'status':'complete',
                    'completion_date': '2015-10-12',
                    'download_url':'http://localhost:5000/orders/order1/LT50290302002123EDC00.tar.gz'
                },
                'LT50310302002123EDC00': {
                    'status':'oncache',
                    'completion_date': None,
                },
                'LT50300302002123EDC00': {
                    'status':'processing',
                    'hadoop_job_id': 'job_abc123',
                    'processing_location': 'processingNode1',
                }
            },
            'products':['tm_sr', 'tm_sr_ndvi', 'tm_toa'],
            'customization': {
                'projection': {
                    'code': 'aea',
                    'standard_parallel_1': 29.5 ,
                    'standard_parallel_2': 45.5,
                    'latitude_of_origin': 23.0,
                    'central_meridian': -96.0,
                    'false_easting': 0.0,
                    'false_northing': 0.0
                },
                'extents': {
                    'north':3164800,
                    'south':3014800,
                    'east':-2415600,
                    'west':-2565600
                },
                'resize': {
                    'pixel_size': 30,
                    'pixel_size_units': 'meters'
                },
                'format': 'gtiff'
            }
        },
        'processing@email.com-101115143201-00132': {
            'status': 'complete',
            'order_source': 'bulk api',
            'priority': 'normal',
            'order_date': '2015-10-11',
            'completion_date': '2015-10-11',
            'note': '',
            'ee_order_id': '',
            'order_type': 'ondemand',
            'initial_email_sent': '2015-10-11',
            'completion_email_sent': '2015-10-11',
            'inputs': {
                'LT50290302002123EDC00': {
                    'status':'complete',
                    'completion_date': '2015-10-12',
                    'download_url':'http://localhost:5000/orders/order1/LT50290302002123EDC00.tar.gz'
                }
             },
            'products':['tm_l1'],
        },
     }   
}


class Storage(object):

    @staticmethod
    def login(username, password):
        return username in app.config['USERS'] and app.config['USERS'][username]['password'] == password

    @staticmethod
    def user_info(username):
        return app.config['USERS'][username]

    @staticmethod
    def list_orders(username):
        orders = app.config['ORDERS'][username]
        return [o for o in orders.keys()]


app = Flask(__name__)
app.config.from_object(__name__)
db = Storage()

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
    

if __name__ == '__main__':
    app.run(host='0.0.0.0')

