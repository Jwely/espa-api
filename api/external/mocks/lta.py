from api.util import chunkify
from api.domain.scene import Scene

def return_update_order_resp(*args, **kwargs):
    class foo(object):
        def success(self):
            return True
    return foo()

def get_user_name(arg1):
    return 'klsmith@usgs.gov'

# product_list is type list, contact_id is type str
# needs to return a dict of dicts
def get_download_urls(product_list, contact_id):
    response = {}
    for item in product_list:
        item_dict = {'lta_prod_code': 'T272'}
        item_dict['sensor'] = 'LANDSAT_8'
        item_dict['status'] = 'available'
        item_dict['download_url'] = 'http://one_time_use.tar.gz'
        response[item] = item_dict
    return response

def update_order_status(ee_order_id, ee_unit_id, something):
    return True, True, True

def order_scenes(product_list, contact_id):
    chunked_list = chunkify(product_list, 3)
    results = dict()
    results["available"] = [p for p in chunked_list[0]]
    results["ordered"] = [p for p in chunked_list[1]]
    results["invalid"] = [p for p in chunked_list[2]]
    results["lta_order_id"] = "tramorderid1"
    return results

def get_available_orders():
    """
    Needs to return:

    response[ordernumber, email, contactid] = [
            {'sceneid':orderingId, 'unit_num':unitNbr},
            {...}
        ]
    """
    ret = {}
    ret[(123, 'klsmith@usgs.gov', 418781)] = [{'sceneid': 'LE70900652008327EDC00',
                                               'unit_num': 789},
                                              {'sceneid': 'LE70900652008327EDC00',
                                               'unit_num': 780}]
    ret[(124, 'klsmith@usgs.gov', 418781)] = [{'sceneid': 'LE70900652008327EDC00',
                                               'unit_num': 780},
                                              {'sceneid': 'LE70900652008327EDC00',
                                               'unit_num': 799}]
    return ret


def get_available_orders_partial1():
    ret = {}
    ret[(125, 'klsmith@usgs.gov', 418781)] = [{'sceneid': 'LE70900652008327EDC00',
                                               'unit_num': 789}]

    return ret


def get_available_orders_partial2():
    ret = {}
    ret[(125, 'klsmith@usgs.gov', 418781)] = [{'sceneid': 'LE70900652008327EDC00',
                                               'unit_num': 789},
                                              {'sceneid': 'LT50900652008327EDC00',
                                               'unit_num': 780}]

    return ret


def sample_tram_order_ids():
    return ('0611512239617', '0611512239618', '0611512239619')

def sample_scene_names():
    return ('LC81370432014073LGN00', 'LC81390422014071LGN00', 'LC81370422014073LGN00')

def get_order_status(tramid):
    response = None
    if tramid == sample_tram_order_ids()[0]:
        response = {'units': [{'sceneid':sample_scene_names()[0], 'unit_status': 'R'}]}
    elif tramid == sample_tram_order_ids()[1]:
        response = {'units': [{'sceneid':sample_scene_names()[1], 'unit_status': 'C'}]}
    elif tramid == sample_tram_order_ids()[2]:
        response = {'units': [{'sceneid':sample_scene_names()[2], 'unit_status': 'R'}]}
    else:
        response = {'units': [{'sceneid': sample_scene_names()[0], 'unit_status': 'C'}]}
    return response
