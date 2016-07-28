class MockAPI(object):

    def fetch_production_products_inputs(self, params):
        return params

    def available_products(self, product_id, username):
        response = {"etm":
                        {"inputs": ["LE70290302003123EDC00"],
                         "outputs": ["etm_sr", "etm_toa",
                                     "etm_l1", "source",
                                     "source_metadata"]}
                    }
        return response

    def get_production_whitelist(self):
        return ['127.0.0.1']




