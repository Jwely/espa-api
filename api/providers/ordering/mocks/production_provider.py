class MockProductionProvider(object):

    def set_product_retry(self, name, orderid, action, msg, msg2, after, limit):
        return True

    def set_product_error(self, name, orderid, action, msg_list):
        return True

