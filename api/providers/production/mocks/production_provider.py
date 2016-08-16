from api.domain.scene import Scene
from api.domain.user import User

class MockProductionProvider(object):

    def set_product_retry(self, name, orderid, processing_loc,
                        error, note, retry_after, retry_limit=None):
        try:
            order_id = Scene.get('order_id', name, orderid)
            assert(type(retry_after) is int)
            assert(type(processing_loc) is str)
            assert(type(error) is str)
            assert(type(note) is str)
        except Exception:
            raise

        return True

    def set_product_error(self, name, orderid, action, msg_list):
        return True

    def respond_true(self, *args, **kwargs):
        return True

    def contact_ids_list(self):
        users = User.where({'id >': 0})
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

    def set_product_error_inputs(self, name, orderid, processing_loc, error):
        return {'name': name, 'orderid': orderid, 'processing_loc': processing_loc,
                'error': error}

    def set_product_unavailable_inputs(self, name, orderid,
                                processing_loc=None, error=None, note=None):
        return {'name': name, 'orderid': orderid, 'processing_loc': processing_loc,
                'error': error, 'note': note}

    def set_mark_product_complete_inputs(self, name, orderid, processing_loc=None,
                                         completed_file_location=None,
                                         destination_cksum_file=None,
                                         log_file_contents=None):
        return {'name': name, 'orderid': orderid, 'processing_loc': processing_loc,
                'completed_file_location': completed_file_location,
                'cksum_file_location': destination_cksum_file,
                'log_file_contents': log_file_contents}

    def queue_products_inputs(self, order_name_tuple_list, processing_location, job_name):
        return {'order_name_tuple_list': order_name_tuple_list,'processing_location': processing_location,
                'job_name': job_name}


