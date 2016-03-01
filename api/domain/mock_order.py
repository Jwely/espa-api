from api.utils import api_cfg
from api.dbconnect import DBConnect
from api.domain.order import Order
from api.domain.scene import Scene
from api.api_logging import api_logger as logger
from psycopg2.extras import Json
import datetime
import os

class MockOrderException(Exception):
    pass

class MockOrder(Order):
    """ Class for interacting with the ordering_order table """

    def __init__(self, **kwargs):
        super(MockOrder, self).__init__(**kwargs)
        try:
            mode = os.environ["espa_api_testing"]
            if mode is not "True":
                raise("MockOrder objects only allowed while testing")
        except:
            raise MockOrderException("MockOrder objects only allowed while testing")

        cfg = api_cfg()

    def __repr__(self):
        return "MockOrder:{0}".format(self.__dict__)

    @classmethod
    def generate_testing_orders(cls):
        # this is the method I'd use to add
        # a number of dummy orders into the test db
        pass

    @classmethod
    def tear_down_testing_orders(cls):
        # method for tearing down orders
        # used for testing
        pass


