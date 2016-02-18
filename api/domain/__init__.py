user_api_operations_v0 = {
    '0': {
        'description': 'Version 0 of the ESPA API',
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

production_api_operations_v0 = {
    '0': {
        'description': 'Version 0 of the ESPA Production API',
        'operations': {
            "/production-api": {
                'function': "list versions",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/production-api/v0": {
                'function': "list operations",
                'methods': [
                    "GET"
                ]
            },
            "/production-api/v0/products?priority=['high'|'normal'|'low']&user='username'&sensor=['modis'|'landsat'|'plot']": {
                'function': "list available products per parameters",
                'methods': [
                    "GET"
                ]
            },
            "/production-api/v0/<orderid>/<productid>": {
                'function': "update product status, completed file locations, etc",
                'comments': 'sceneids should be delivered in the product_ids parameter, comma separated if more than one',
                'methods': [
                    "PUT"
                ]
            },
            "/production-api/v0/configuration/<key>": {
                'function': "list value for specified configuration key",
                'methods': [
                    "GET"
                ]
            },
        }
    }
}

api_operations_v0 = {"user": user_api_operations_v0, "production": production_api_operations_v0}

default_error_message = {"msg": "there's been a problem retrieving your information. admins have been notified"}





