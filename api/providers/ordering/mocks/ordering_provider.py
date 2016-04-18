class MockOrderingProvider(object):

    def fetch_user_orders(self, userid, filters={}):
        orders = ['1', '2']
        return {'orders': orders}
