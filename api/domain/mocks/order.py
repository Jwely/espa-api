from api.util import api_cfg
from api.util.dbconnect import DBConnect
from api.domain.order import Order
from api.domain.scene import Scene
from api.domain.user import User
from api.util import chunkify
from test.version0_testorders import build_base_order
from api.providers.ordering.ordering_provider import OrderingProvider
import os

class MockOrderException(Exception):
    pass

class MockOrder(object):
    """ Class for interacting with the ordering_order table """

    def __init__(self):
        try:
            mode = os.environ["espa_api_testing"]
            if mode is not "True":
                raise("MockOrder objects only allowed while testing")
        except:
            raise MockOrderException("MockOrder objects only allowed while testing")
        self.base_order = build_base_order()
        self.cfg = api_cfg()
        self.ordering_provider = OrderingProvider()

    def __repr__(self):
        return "MockOrder:{0}".format(self.__dict__)

    def generate_testing_order(self, user_id):
        user = User.where("id = {0}".format(user_id))[0]
        orderid = self.ordering_provider.place_order(self.base_order, user)
        order = Order.where("orderid = '{0}'".format(orderid))[0]
        return order.id

    def tear_down_testing_orders(self):
        # delete scenes first
        scene_sql = "DELETE FROM ordering_scene where id > 0;"
        with DBConnect(**self.cfg) as db:
            db.execute(scene_sql)
            db.commit()
        # now you can delete orders
        ord_sql = "DELETE FROM ordering_order where id > 0;"
        with DBConnect(**self.cfg) as db:
            db.execute(ord_sql)
            db.commit()
        return True

    def update_scenes(self, order_id, attribute, values):
        scenes = Scene.where("order_id = {0}".format(order_id))
        xscenes = chunkify(scenes, len(values))

        for idx, value in enumerate(values):
            for scene in xscenes[idx]:
                scene.update(attribute, value)
        return True
