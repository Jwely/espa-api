user_api_operations = {
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
    },
    '1': {
        'description': 'Version 1 of the ESPA API',
        'operations': {
            "/api": {
                'function': "list versions",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/api/v1": {
                'function': "list operations",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/api/v1/available-products/<product_ids>": {
                'function': "list available products per sceneid",
                'comments': "comma separated ids supported",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/api/v1/available-products": {
                'function': "list available products per sceneid",
                'comments': 'sceneids should be delivered in the product_ids parameter, comma separated if more than one',
                'methods': [
                    "HEAD",
                    "POST"
                ]
            },
            "/api/v1/projections": {
                'function': "list available projections",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/api/v1/formats": {
                'function': "list available output formats",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/api/v1/resampling-methods": {
                'function': "list available resampling methods",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/api/v1/orders": {
                'function': "list orders for authenticated user",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/api/v1/orders/<email>": {
                'function': "list orders for supplied email, for user collaboration",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/api/v1/order/<ordernum>": {
                'function': "retrieves a submitted order",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/api/v1/request/<ordernum>": {
                'function': "retrieve order sent to server",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/api/v1/order": {
                'function': "point for accepting processing requests via HTTP POST with JSON body. Errors are returned to user, successful validation returns an orderid",
                'methods': [
                    "POST"
                ]
            },
        }
    }
}

production_api_operations = {
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
    },
    '1': {
        'description': 'Version 1 of the ESPA Production API',
        'operations': {
            "/production-api": {
                'function': "list versions",
                'methods': [
                    "HEAD",
                    "GET"
                ]
            },
            "/production-api/v1": {
                'function': "list operations",
                'methods': [
                    "GET"
                ]
            },
            "/production-api/v1/products?priority=['high'|'normal'|'low']&user='username'&sensor=['modis'|'landsat'|'plot']": {
                'function': "list available products per parameters",
                'methods': [
                    "GET"
                ]
            },
            "/production-api/v1/<orderid>/<productid>": {
                'function': "update product status, completed file locations, etc",
                'comments': 'sceneids should be delivered in the product_ids parameter, comma separated if more than one',
                'methods': [
                    "PUT"
                ]
            },
            "/production-api/v1/configuration/<key>": {
                'function': "list value for specified configuration key",
                'methods': [
                    "GET"
                ]
            },
        }
    }
}

admin_api_operations = {
    '0': {
        'description': 'Version 0 of the admin api',
        'operations': {
            '/api/v0/reports': {
                'function': 'list available reports',
                'methods': [
                    'GET'
                ]
            },
            '/api/v0/reports/<reportname>': {
                'function': 'generate report',
                'methods': [
                    'GET'
                ]
            },
            '/api/v0/statistics/': {
                'function': 'list available statistics',
                'methods': [
                    'GET'
                ]
            },
            '/api/v0/statistics/<name>': {
                'function': 'calculate statistic',
                'methods': [
                    'GET'
                ]
            },
            '/api/v0/system-status': {
                'function': 'get system status message',
                'methods': [
                    'GET'
                ]
            },
            '/api/v0/system-status-update': {
                'function': 'update the system status',
                'methods': [
                    'POST'
                ]
            },
            '/api/v0/system/config': {
                'function': 'retrieve config variables',
                'methods': [
                    'GET'
                ]
            },
        }
    },
    '1': {
        'description': 'Version 1 of the admin api',
        'operations': {
            '/api/v1/reports': {
                'function': 'list available reports',
                'methods': [
                    'GET'
                ]
            },
            '/api/v1/reports/<reportname>': {
                'function': 'generate report',
                'methods': [
                    'GET'
                ]
            },
            '/api/v1/statistics/': {
                'function': 'list available statistics',
                'methods': [
                    'GET'
                ]
            },
            '/api/v1/statistics/<name>': {
                'function': 'calculate statistic',
                'methods': [
                    'GET'
                ]
            },
            '/api/v1/system-status': {
                'function': 'get system status message',
                'methods': [
                    'GET'
                ]
            },
            '/api/v1/system-status-update': {
                'function': 'update the system status',
                'methods': [
                    'POST'
                ]
            },
            '/api/v1/system/config': {
                'function': 'retrieve config variables',
                'methods': [
                    'GET'
                ]
            },
        }
    }
}


api_operations = {"user": user_api_operations, "production": production_api_operations}

default_error_message = {"msg": "there's been a problem retrieving your information. admins have been notified"}


def format_sql_params(base_sql, params):
    where_list = list()

    # params coming in as lists from espa-web (json)
    # need to be converted to a tuple
    for key, val in params.iteritems():
        if isinstance(val, list):
            params[key] = tuple(val)

    fields, values = zip(*params.items())

    for index, value in enumerate(fields):
        if isinstance(values[index], tuple):
            _operator = " in "
        elif " " in value:
            _operator = ""
        else:
            _operator = " = "

        where_list.append(" {} ".format(value) + _operator + " %s ")

    sql = base_sql + " AND ".join(where_list)
    return sql, values





