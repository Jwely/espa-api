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
        return username in USERS and USERS[username]['password'] == password

    @staticmethod
    def user_info(username):
        return USERS[username]

    @staticmethod
    def list_orders(username):
        orders = ORDERS[username]
        return [o for o in orders.keys()]


'''class DBStorage(Storage):

    def __init__(self, connection):
        self.connection = connection

    def initialize(self):
        with self.connection as cursor:
            with open('db/schema.sql', 'r') as schema:
                cursor.execute(schema.read())
        
    def login(username, password):
        pass

    def user_info(username):
        pass

    def list_orders(username):
        pass        
'''
