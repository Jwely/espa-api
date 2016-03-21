from api.domain.scene import Scene
from api.domain.user import User

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

    def contact_ids_list(self):
        users = User.where("id > 0")
        return [u.contactid for u in users]

    def get_products_to_process_inputs(self, record_limit=500,
                                for_user=None,
                                priority=None,
                                product_types=['landsat', 'modis'],
                                encode_urls=False):
        return {'record_limit': record_limit, 'for_user': for_user, 'priority': priority,
                'product_types': product_types, 'encode_urls': encode_urls}

    def update_status_inputs(self, name, orderid,
                        processing_loc=None, status=None):
        response = {'name': name, 'orderid': orderid,
                    'processing_loc': processing_loc,
                    'status': status}

        return response
