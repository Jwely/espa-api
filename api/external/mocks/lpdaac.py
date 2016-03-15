def get_download_urls(modis_list):
    response = {}
    for item in modis_list:
        response[item] = {}
        response[item]['download_url'] = 'http://some.download.url.tar.gz'
    return response

def input_exists_true(input):
    return True

def input_exists_false(input):
    return False