class Configuration(object):

    def __init__(self, use_cache=True):
        self.use_cache = use_cache

    def get(self, key):
        raise NotImplementedError

    def put(self, key, value):
        raise NotImplementedError

    def mget(self, keys):
        raise NotImplementedError

    def mput(self, kv_dict):
        raise NotImplementedError

    def mdelete(self, keys):
        raise NotImplementedError

    def exists(self, key):
        raise NotImplementedError

    def load(self, config):
        raise NotImplementedError

    def dump(self, path):
        raise NotImplementedError
