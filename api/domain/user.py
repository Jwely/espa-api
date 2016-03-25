import sys
import time
import traceback
import datetime

from api.external import lta
from api.util.dbconnect import db_instance
from validate_email import validate_email

from api.system.logger import ilogger as logger

class UserException(Exception):
    pass

class User(object):

    base_sql = "SELECT username, email, first_name, last_name, contactid "\
                "FROM auth_user WHERE "

    def __init__(self, username, email, first_name, last_name, contactid):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.contactid = contactid

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
        self.id = User.find_or_create_user(self.username, self.email, self.first_name, self.last_name, self.contactid)


    @classmethod
    def get(cls, username, password):
        user_tup = None
        try:
            lta_user = lta.get_user_info(username, password)
            contactid = lta.login_user(username, password)
        except:
            exc_type, exc_val, exc_trace = sys.exc_info()
            logger.debug("ERR retrieving user from lta, username: {0}\n exception {1}".format(username, traceback.format_exc()))
            raise exc_type, exc_val, exc_trace

        return (str(username), str(lta_user.email), str(lta_user.first_name), str(lta_user.last_name), str(contactid))

    @classmethod
    def find_or_create_user(cls, username, email, first_name, last_name, contactid):
        user_id = None
        nownow = time.strftime('%Y-%m-%d %H:%M:%S')
        insert_stmt = "insert into auth_user (username, " \
                      "email, first_name, last_name, password, " \
                      "is_staff, is_active, is_superuser, " \
                      "last_login, date_joined, contactid) values {};"
        arg_tup = (username, email, first_name, last_name,
                    'pass', 'f', 't', 'f', nownow, nownow, contactid)

        with db_instance() as db:
            user_sql = "select id from auth_user where username = %s;"
            db.select(user_sql, username)
            if len(db) == 0:
                # we need to create a local user
                db.execute(insert_stmt.format(arg_tup))
                db.commit()
            # user should be there now, lets try this again
            db.select(user_sql, username)
            try:
                user_id = db[0]['id']
            except:
                exc_type, exc_val, exc_trace = sys.exc_info()
                logger.debug("ERR user find_or_create args {0} {1} " \
                             "{2} {3}\n trace: {4}".format(username, email, first_name,
                                                           last_name, traceback.format_exc()))
                raise exc_type, exc_val, exc_trace

        return user_id

    @classmethod
    def where(cls, params):
        sql = [str(cls.base_sql)]
        if isinstance(params, list):
            param_str = " AND ".join(params)
            sql.append(param_str)
        elif isinstance(params, str):
            sql.append(params)
        else:
            raise UserException("User.where arg needs to be a list or a str")

        sql.append(";")
        sql = " ".join(sql)
        with db_instance() as db:
            db.select(sql)
            returnlist = []
            for i in db:
                obj = User(i["username"], i["email"], i["first_name"], i["last_name"], i["contactid"])
                returnlist.append(obj)

        return returnlist

    def update(self, att, val):
        self.__setattr__(att, val)
        if isinstance(val, str) or isinstance(val, datetime.datetime):
            val = "\'{0}\'".format(val)
        sql = "update auth_user set {0} = {1} where id = {2};".format(att, val, self.id)
        with db_instance() as db:
            db.execute(sql)
            db.commit()
        return True

    def roles(self):
        result = None
        with db_instance() as db:
            db.select("select is_staff, is_active, is_superuser from auth_user where id = %s;" % self.id)
        try:
            result = db[0]
        except:
            exc_type, exc_val, exc_trace = sys.exc_info()
            logger.debug("ERR retrieving roles for user. msg{0} trace{1}".format(exc_val, traceback.format_exc()))
            raise exc_type, exc_val, exc_trace

        return result

    def is_staff(self):
        return self.roles()['is_staff']

    def active(self):
        # is_active is already a method of UserMixin
        return self.roles()['is_active']

    def is_superuser(self):
        return self.roles()['is_superuser']

    def role_list(self):
        out_list = []
        if self.is_staff():
            out_list.append('staff')
        if self.is_superuser():
            out_list.append('super')
        if self.active():
            out_list.append('active')

        return out_list

    def as_dict(self):
        return {"email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "username": self.username,
                "roles": self.role_list()}

