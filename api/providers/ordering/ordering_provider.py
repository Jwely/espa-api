from api.domain import sensor

class OrderingProvider(object):
    def api_versions(self):
        info_dict = {
            "version_0": {
                "description": "Demo URLs for development",
                "url": "/api/v0"
            } 
        }

        return info_dict

    def api_info(self, version):
        info_dict = {
            '0': {
                'description': 'Version 0 of the ESPA API',
                'base_url': '/api/v0',
                'operations': {
                    "/api": {
                        'function': "list versions",
                        'methods': [
                            "HEAD",
                            "GET"
                        ]
                    },
                    "/api/v0": {
                        'function': "list operations",
                        'methods': [
                            "HEAD",
                            "GET"
                        ]
                    },
                    "/api/v0/available-products/<product_ids>": {
                        'function': "list available products per sceneid",
                        'comments': "comma separated ids supported",
                        'methods': [
                            "HEAD",
                            "GET"
                        ]
                    },
                    "/api/v0/available-products": {
                        'function': "list available products per sceneid",
                        'comments': 'sceneids should be delivered in the product_ids parameter, comma separated if more than one',
                        'methods': [
                            "HEAD",
                            "POST"
                        ]
                    },
                    "/api/v0/projections": {
                        'function': "list available projections",
                        'methods': [
                            "HEAD",
                            "GET"
                        ]
                    },
                    "/api/v0/formats": {
                        'function': "list available output formats",
                        'methods': [
                            "HEAD",
                            "GET"
                        ]
                    },
                    "/api/v0/resampling-methods": {
                        'function': "list available resampling methods",
                        'methods': [
                            "HEAD",
                            "GET"
                        ]
                    },
                    "/api/v0/orders": {
                        'function': "list orders for authenticated user",
                        'methods': [
                            "HEAD",
                            "GET"
                        ]
                    },
                    "/api/v0/orders/<email>": {
                        'function': "list orders for supplied email, for user collaboration",
                        'methods': [
                            "HEAD",
                            "GET"
                        ]
                    },
                    "/api/v0/order/<ordernum>": {
                        'function': "retrieves a submitted order",
                        'methods': [
                            "HEAD",
                            "GET"
                        ]
                    },
                    "/api/v0/request/<ordernum>": {
                        'function': "retrieve order sent to server",
                        'methods': [
                            "HEAD",
                            "GET"
                        ]
                    },

                    "/api/v0/order": {
                        'function': "point for accepting processing requests via HTTP POST with JSON body. Errors are returned to user, successful validation returns an orderid",
                        'methods': [
                            "POST"
                        ]
                    },
                }
            }
        }

        if info_dict.__contains__(version):
            response = info_dict[version]
        else:
            ver_str = ", ".join(info_dict.keys())
            err_msg = "%s is not a valid api version, these are: %s" % (version, ver_str)
            response = {"errmsg": err_msg} 

        return response 

    def available_products(self, product_id):
        prod_list = product_id.split(",")
        return sensor.available_products(prod_list)

    def place_order(self, username):
        pass

    def list_orders(self, username_or_email):
        pass

    def view_order(self, orderid):
        pass

    def order_status(self, orderid):
        pass

    def item_status(self, orderid, itemid='ALL'):
        """

        :rtype: str
        """
        pass
