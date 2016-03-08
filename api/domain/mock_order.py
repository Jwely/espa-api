from api.domain.utils import api_cfg
from api.domain.dbconnect import DBConnect
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
    def check_test_database_presence(cls):
        pass

    @classmethod
    def generate_testing_orders(cls):
        cls.check_test_database_presence()


    @classmethod
    def tear_down_testing_orders(cls):
        # method for tearing down orders
        # used for testing
        pass



