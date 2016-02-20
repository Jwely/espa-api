""" Holds domain objects for orders and the items attached to them """

from api.utils import api_cfg
from api.dbconnect import DBConnect
import datetime

cfg = api_cfg()

class Order(object):
    """ Class for interacting with the ordering_order table """

    def __init__(self, oid):
        """
        Args:
        id (int): primary key for the order to be retrieved
        """
        obj = None
        with DBConnect(**cfg) as db:
            sql = "select * from ordering_order where id = {0};".format(oid)
            db.select(sql)
            obj = db[0]

        for k, v in obj.iteritems():
            setattr(self, k, v)

    def __repr__(self):
        return "Order:{0}".format(self.__dict__)

    def to_dict(self):
        """ x """
        pass

    @classmethod
    def where(cls, att=None, val=None):
        sql = "select id from ordering_order where {0} = "
        if isinstance(val, str):
            sql += "'{1}';"
        else:
            sql += "{1};"
        sql = sql.format(att, val)
        with DBConnect(**cfg) as db:
            db.select(sql)
            returnlist = []
            for i in db:
                obj = Order(i['id'])
                returnlist.append(obj)

        return returnlist

    def user_email(self):
        sql = "select email from auth_user where id = {0};".format(self.user_id)
        with DBConnect(**cfg) as db:
            db.select(sql)
            return db[0]['email']

    def update(self, att, val):
        if isinstance(val, str) or isinstance(val, datetime.datetime):
            val = "'{0}'".format(val)
        self.__setattr_(att, val)
        sql = "update ordering_order set {0} = {1} where id = {2};".format(att, val, self.id)
        with DBConnect(**cfg) as db:
            db.execute(sql)
            db.commit()

    @staticmethod
    def from_dict(dadsf):
        """ x """
        pass

    def validate(self):
        """ checks that this object was constructed correctly

        Raises:
            ValidationException if incorrect parameters specified
        """
        #registry.validation.validate(self)
        pass
