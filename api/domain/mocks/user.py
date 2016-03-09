import os
from api.util import api_cfg
from api.domain.user import User
from api.util.dbconnect import DBConnect

class MockUserException(Exception):
    pass

class MockUser(object):
    ''' class for mocking the User class in unit tests '''

    def __init__(self):
        try:
            mode = os.environ['espa_api_testing']
            if mode is not 'True':
                raise MockUserException("MockUser objects only allowed while testing")
        except:
            raise MockUserException("MockUser objects only allowed while testing")

        self.cfg = api_cfg()

    def __repr__(self):
        return "MockUser: {0}".format(self.__dict__)

    def add_testing_user(self):
        ''' add user record to test schemas auth_user table '''
        user = User.find_or_create_user('bilbo_baggins', 'bilbo@usgs.gov',
                                 'bilbo', 'baggins', '123456')
        return user

    def cleanup(self):
        sql = "DELETE from auth_user where id > 0;"
        with DBConnect(**self.cfg) as db:
            db.execute(sql)
            db.commit()