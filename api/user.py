import time
import psycopg2
from flask.ext.login import UserMixin

from api import lta
from api.dbconnect import DBConnect
from api.utils import api_cfg
from validate_email import validate_email

class User(UserMixin):

    def __init__(self, username, email, first_name, last_name):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

        @property
        def username(self):
            return self._username

        @username.setter
        def username(self, value):
            if not isinstance(value, str):
                raise TypeError('Expected a string')
            self._username = value

        @property
        def first_name(self):
            return self._first_name

        @first_name.setter
        def first_name(self, value):
            if not isinstance(value, str):
                raise TypeError('Expected a string')
            self._first_name = value

        @property
        def last_name(self):
            return self._last_name

        @last_name.setter
        def last_name(self, value):
            if not isinstance(value, str):
                raise TypeError('Expected a string')
            self._last_name = value

        @property
        def email(self):
            return self._email

        @email.setter
        def email(self, value):
            if not validate_email(value):
                raise StandardError('user email value invalid')
            self._email = value

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

        with DBConnect(**api_cfg()) as db:
            user_sql = "select id from auth_user where username = %s;"
            db.select(user_sql, username)
            if len(db) == 0:
                # we need to create a local user
                db.execute(insert_stmt.format(arg_tup))
                db.commit()
            # user should be there now, lets try this again
            db.select(user_sql, username)
            user_id = db[0]['id']

        return user_id

