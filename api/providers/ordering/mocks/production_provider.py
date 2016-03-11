from api.domain.scene import Scene


class MockProductionProvider(object):

    def set_product_retry(self, name, orderid, processing_loc,
                        error, note, retry_after, retry_limit=None):
        try:
            order_id = Scene.get('order_id', name=name, orderid=orderid)
            assert(type(retry_after) is int)
            assert(type(processing_loc) is str)
            assert(type(error) is str)
            assert(type(note) is str)
        except Exception, e:
            raise(e.message)

        return True

    def set_product_error(self, name, orderid, action, msg_list):
        return True

    def respond_true(self, *args, **kwargs):
        return True