from api.util import chunkify

def get_user_name(arg1):
    return arg1

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
    return True

def order_scenes(product_list, contact_id):
    chunked_list = chunkify(product_list, 3)

    results = dict()
    results["available"] = [p.name for p in chunked_list[0]]
    results["ordered"] = [p.name for p in chunked_list[1]]
    results["invalid"] = [p.name for p in chunked_list[2]]
    results["lta_order_id"] = "tramorderid1"
    return results




