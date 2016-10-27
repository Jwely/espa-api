# espa-api

Version 1.0.0
=============
This is an API for interacting with the ESPA ordering system.

## Related Pages
* [ESPA System Overview] (docs/OVERVIEW.md)
* [Available Products](docs/AVAILABLE-PRODUCTS.md)
* [Abbreviations & Definitions](docs/TERMS.md)
* [ESPA Customizations](docs/CUSTOMIZATION.md)

## User API
The User API is public facing and available for anyone to code and interact with.  Version 1 provides the minimum functionality necessary to place orders, view order status, and determine available products from a list of inputs. There are endpoints for providing available projections, resampling methods, and output formats.

All user interactions with API functions must be accompanied by valid credentials. Accounts are managed in the USGS ERS system https://ers.cr.usgs.gov/register/

The api host is https://espa.cr.usgs.gov . 

### User API Operations

**GET /api**

Lists all available versions of the api.
```json
curl --user username:password https://espa.cr.usgs.gov/api

{
    "versions": {
        "0": {
            "description": "First release of the ESPA API"
        }
    }
}
```

**GET /api/v0**

Lists all available api operations.
```json
curl --user username:password https://espa.cr.usgs.gov/api/v0
{
    "description": "Version 0 of the ESPA API",
    "operations": {
        "/api": {
            "function": "list versions",
            "methods": [
                "HEAD",
                "GET"
            ]
        },
        "/api/v0": {
            "function": "list operations",
            "methods": [
                "HEAD",
                "GET"
            ]
        },
        "/api/v0/available-products": {
            "comments": "sceneids should be delivered in the product_ids parameter, comma separated if more than one",
            "function": "list available products per sceneid",
            "methods": [
                "HEAD",
                "POST"
            ]
        },
        "/api/v0/available-products/<product_ids>": {
            "comments": "comma separated ids supported",
            "function": "list available products per sceneid",
            "methods": [
                "HEAD",
                "GET"
            ]
        },
        "/api/v0/formats": {
            "function": "list available output formats",
            "methods": [
                "HEAD",
                "GET"
            ]
        },
            "/api/v0/order": {
            "function": "point for accepting processing requests via HTTP POST with JSON body. Errors are returned to user, successful validation returns an orderid",
            "methods": [
                "POST"
            ]
        },
        "/api/v0/order/<ordernum>": {
            "function": "retrieves a submitted order",
            "methods": [
                "HEAD",
                "GET"
            ]
        },
        "/api/v0/orders": {
            "function": "list orders for authenticated user",
            "methods": [
                "HEAD",
                "GET"
            ]
        },
        "/api/v0/orders/<email>": {
            "function": "list orders for supplied email, for user collaboration",
            "methods": [
                "HEAD",
                "GET"
            ]
        },
        "/api/v0/projections": {
            "function": "list available projections",
            "methods": [
                "HEAD",
                "GET"
            ]
        },
        "/api/v0/resampling-methods": {
            "function": "list available resampling methods",
            "methods": [
                "HEAD",
                "GET"
            ]
        }
    }
}
```

**GET /api/v0/user**

Returns user information for the authenticated user.
```json
curl --user username:password https://espa.cr.usgs.gov/api/v0/user

{
  "email": "production@email.com",
  "first_name": "Production",
  "last_name": "Person",
  "roles": [
    "user",
    "production"
  ],
  "username": "production"
}
```
   
**GET /api/v0/available-products/\<product_id\>**

Lists the available output products for the supplied input.
```json
curl --get --user username:password https://espa.cr.usgs.gov/api/v0/available-products/LE70290302003123EDC00
{
    "etm7": {
        "inputs": [
            "LE70290302003123EDC00"
        ], 
        "products": [
            "source_metadata", 
            "l1", 
            "toa", 
            "bt", 
            "cloud", 
            "sr", 
            "lst", 
            "swe", 
            "sr_ndvi", 
            "sr_evi", 
            "sr_savi", 
            "sr_msavi", 
            "sr_ndmi", 
            "sr_nbr", 
            "sr_nbr2", 
            "stats"
        ]
    }
}
```

**POST /api/v0/available-products**

Lists available products for the supplied inputs.  Also classifies the inputs by sensor or lists as 'not implemented' if the values cannot be ordered or determined.
```json
curl  --user username:password -d '{"inputs":["LE70290302003123EDC00",
               "MOD09A1.A2000073.h12v11.005.2008238080250.hdf", "bad_scene_id"]}' https://espa.cr.usgs.gov/api/v0/available-products
{
    "etm7": {
        "inputs": [
            "LE70290302003123EDC00"
        ], 
        "products": [
            "source_metadata", 
            "l1", 
            "toa", 
            "bt", 
            "cloud", 
            "sr", 
            "lst", 
            "swe", 
            "sr_ndvi", 
            "sr_evi", 
            "sr_savi", 
            "sr_msavi", 
            "sr_ndmi", 
            "sr_nbr", 
            "sr_nbr2", 
            "stats"
        ]
    }, 
    "mod09a1": {
        "inputs": [
            "MOD09A1.A2000073.h12v11.005.2008238080250.hdf"
        ], 
        "outputs": [
            "l1", 
            "stats"
        ]
    }, 
    "not_implemented": [
        "bad_scene_id"
    ]
}
```

**GET /api/v0/projections**

Lists and describes available projections.  This is a dump of the schema defined that constrains projection info.
```json
curl --get --user username:password https://espa.cr.usgs.gov/api/v0/projections
{
    "aea": {
        "properties": {
            "central_meridian": {
                "maximum": 180, 
                "minimum": -180, 
                "required": true, 
                "type": "number"
            }, 
            "datum": {
                "enum": [
                    "wgs84", 
                    "nad27", 
                    "nad83"
                ], 
                "required": true, 
                "type": "string"
            }, 
            "false_easting": {
                "required": true, 
                "type": "number"
            }, 
            "false_northing": {
                "required": true, 
                "type": "number"
            }, 
            "latitude_of_origin": {
                "maximum": 90, 
                "minimum": -90, 
                "required": true, 
                "type": "number"
            }, 
            "standard_parallel_1": {
                "maximum": 90, 
                "minimum": -90, 
                "required": true, 
                "type": "number"
            }, 
            "standard_parallel_2": {
                "maximum": 90, 
                "minimum": -90, 
                "required": true, 
                "type": "number"
            }
        },
        "type": "object"
    }, 
    "lonlat": {
        "type": "null"
    }, 
    "ps": {
        "properties": {
            "false_easting": {
                "required": true, 
                "type": "number"
            }, 
            "false_northing": {
                "required": true, 
                "type": "number"
            }, 
            "latitude_true_scale": {
                "abs_rng": [
                    60, 
                    90
                ], 
                "required": true, 
                "type": "number"
            }, 
            "longitudinal_pole": {
                "maximum": 180, 
                "minimum": -180, 
                "required": true, 
                "type": "number"
            }
        }, 
        "type": "object"
    }, 
    "sinu": {
        "properties": {
            "central_meridian": {
                "maximum": 180, 
                "minimum": -180, 
                "required": true, 
                "type": "number"
            }, 
            "false_easting": {
                "required": true, 
                "type": "number"
            }, 
            "false_northing": {
                "required": true, 
                "type": "number"
            }
        }, 
        "type": "object"
    },
    "utm": {
        "properties": {
            "zone": {
                "maximum": 60, 
                "minimum": 1, 
                "required": true, 
                "type": "integer"
            }, 
            "zone_ns": {
                "enum": [
                    "north", 
                    "south"
                ], 
                "required": true, 
                "type": "string"
            }
        }, 
        "type": "object"
    }
}        
```

**GET /api/v0/formats**

Lists all available output formats
```json
curl --user username:password https://espa.cr.usgs.gov/api/v0/formats

{
  "formats": [
    "gtiff", 
    "hdf-eos2", 
    "envi"
  ]
}
```

**GET /api/v0/resampling-methods**

Lists all available resampling methods
```json
curl --user username:password https://espa.cr.usgs.gov/api/v0/resampling-methods

{
  "resampling_methods": [
    "nn", 
    "bil", 
    "cc"
  ]
}
```

**GET /api/v0/list-orders**

List orders for the authenticated user.
```json
curl --user username:password https://espa.cr.usgs.gov/api/v0/list-orders

{
  "orders": [
    "production@email.com-101015143201-00132", 
    "production@email.com-101115143201-00132"
  ]
}
```

**GET /api/v0/list-orders/\<email\>**

Lists orders for the supplied email.  Necessary to support user collaboration.
```json
curl --user username:password https://espa.cr.usgs.gov/api/v0/list-orders/production@email.com

{
  "orders": [
    "production@email.com-101015143201-00132", 
    "production@email.com-101115143201-00132"
  ]
}
```

**GET /api/v0/order-status/\<ordernum\>**

Retrieves a submitted orders status

```json
{
 "orderid": "production@usgs.gov-07282016-135122",
 "status": "complete"
}
```

**GET /api/v0/order/\<ordernum\>**

Retrieves details for a submitted order. Some information may be omitted from this response depending on access privileges.
```json
curl --user username:password https://espa.cr.usgs.gov/api/v0/order/production@usgs.gov-03072016-081013
{
  "completion_date": "2016-08-01T14:47:08.589621",
  "note": "",
  "order_date": "2016-08-01T14:17:48.589621",
  "order_source": "espa",
  "order_type": "level2_ondemand",
  "orderid": "production@usgs.gov-03072016-081013",
  "priority": "normal",
  "product_options": null,
  "product_opts": {
    "format": "gtiff",
    "tm5": {
      "inputs": [
        "LT50380322011299PAC01"
      ],
      "products": [
        "sr"
      ]
    }
  },
  "status": "complete"
}
```

**GET /api/v0/item-status/\<ordernum\>**

Retrieve the status and details for all products in an order.
```json
curl --user username:password https://espa.cr.usgs.gov/api/v0/item-status/production@usgs.gov-03072016-081013

{
 "orderid": {
             "production@usgs.gov-07282016-135122": [
                {
                       "cksum_download_url": "http://espa.cr.usgs.gov/orders/production@usgs.gov-07282016-135122/LO82111132014063-SC20160728135757.md5",
                       "completion_date": "2016-08-01T14:17:08.589621",
                       "name": "LO82111132014063LGN00",
                       "note": "",
                       "product_dload_url": "http://espa.cr.usgs.gov/orders/production@usgs.gov-07282016-135122/LO82111132014063-SC20160728135757.tar.gz",
                       "status": "complete"
                },
                {
                       "cksum_download_url": "http://espa.cr.usgs.gov/orders/production@usgs.gov-08042016-120321-382/LT50190392010051-SC20160804121126.md5",
                       "completion_date": "2016-08-01T14:17:08.589621",
                       "name": "LT50190392010051GNC01",
                       "note": "",
                       "product_dload_url": "http://espa.cr.usgs.gov/orders/production@usgs.gov-08042016-120321-382/LT50190392010051-SC20160804121126.tar.gz",
                       
                       "status": "complete"
                }
             ]
         }
 }

```

**GET /api/v0/item-status/\<ordernum\>/\<itemnum\>**

Retrieve status and details for a particular product in an order
```json
curl --user username:password https://espa.cr.usgs.gov/api/v0/item-status/production@usgs.gov-03072016-081013/LO82111132014063LGN00

{
 "orderid": {
             "production@usgs.gov-07282016-135122": [
                {
                       "cksum_download_url": "http://espa.cr.usgs.gov/orders/production@usgs.gov-07282016-135122/LO82111132014063-SC20160728135757.md5",
                       "completion_date": "2016-08-01T14:17:08.589621",
                       "name": "LO82111132014063LGN00",
                       "note": "",
                       "product_dload_url": "http://espa.cr.usgs.gov/orders/production@usgs.gov-07282016-135122/LO82111132014063-SC20160728135757.tar.gz",
                       "status": "complete"
                }
             ]
         }
 }

```

**POST /api/v0/order**

Accepts requests for process from an HTTP POST with a JSON body.  The body is validated and any errors are returned to the caller.  Otherwise, an orderid is returned.
```json

curl --user username:password -d '{"olitirs8": {
                                                    "inputs": ["LC80270292015233LGN00"], 
                                                    "products": ["sr"]
                                                 }, 
                                     "format": "gtiff", 
                                     "resize": {
                                                "pixel_size": 60, 
                                                "pixel_size_units": "meters"
                                                }, 
                                     "resampling_method": "nn", 
                                     "plot_statistics": true, 
                                     "projection": {
                                                    "aea": {
                                                            "standard_parallel_1": 29.5,
                                                            "standard_parallel_2": 45.5,
                                                            "central_meridian": -96.0,
                                                            "latitude_of_origin": 23.0,
                                                            "false_easting": 0.0,
                                                            "false_northing": 0.0,
                                                            "datum": "wgs84"
                                                            }
                                                    },
                                     "image_extents": {
                                                        "north": 0.0002695,
                                                        "south": 0,
                                                        "east": 0.0002695,
                                                        "west": 0,
                                                        "units": "dd"
                                                    },
                                     "note": "this is going to be sweet..."
                                     }' https://espa.cr.usgs.gov/api/v0/order

Returns:
{
    "orderid": "production@email.com-101015143201-00132"
}
```


**GET /api/v0/order-schema**
 
Retrieves order schema definition
```javascript
curl --user username:password https://espa.cr.usgs.gov/api/v0/order-schema

{"oneormoreobjects": ["myd09gq",
                       "myd09ga",
                       "oli8",
                       "myd13q1",
                       "tm4",
                       "tm5",
                       "etm7",
                       "mod13a1",
                       "mod13a2",
                       "mod13a3",
                       "mod09a1",
                       "mod09ga",
                       "myd13a2",
                       "myd13a3",
                       "olitirs8",
                       "myd13a1",
                       "mod13q1",
                       "myd09q1",
                       "mod09q1",
                       "myd09a1",
                       "mod09gq"],
 "properties": {"etm7": {"properties": {"inputs": {"ItemCount": "inputs",
                                                       "items": {"pattern": "^le7\\d{3}\\d{3}\\d{4}\\d{3}\\w{3}.{2}$",
                                                                  "type": "string"},
                                                       "minItems": 1,
                                                       "required": True,
                                                       "type": "array",
                                                       "uniqueItems": True},
                                           "products": {"items": {"enum": ["source_metadata",
                                                                              "l1",
                                                                              "toa",
                                                                              "bt",
                                                                              "cloud",
                                                                              "sr",
                                                                              "lst",
                                                                              "swe",
                                                                              "sr_ndvi",
                                                                              "sr_evi",
                                                                              "sr_savi",
                                                                              "sr_msavi",
                                                                              "sr_ndmi",
                                                                              "sr_nbr",
                                                                              "sr_nbr2",
                                                                              "stats"],
                                                                    "type": "string"},
                                                         "minItems": 1,
                                                         "required": True,
                                                         "restricted": True,
                                                         "stats": True,
                                                         "type": "array",
                                                         "uniqueItems": True}},
                           "type": "object"},
                 "format": {"enum": ["gtiff", "hdf-eos2", "envi"],
                             "required": True,
                             "type": "string"},
                 "image_extents": {"dependencies": ["projection"],
                                    "extents": 200000000,
                                    "properties": {"east": {"required": True,
                                                              "type": "number"},
                                                    "north": {"required": True,
                                                               "type": "number"},
                                                    "south": {"required": True,
                                                               "type": "number"},
                                                    "units": {"enum": ["dd",
                                                                         "meters"],
                                                               "required": True,
                                                               "type": "string"},
                                                    "west": {"required": True,
                                                              "type": "number"}},
                                    "type": "object"},
                 "mod09a1": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^mod09a1\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "mod09ga": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^mod09ga\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "mod09gq": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^mod09gq\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "mod09q1": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^mod09q1\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "mod13a1": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^mod13a1\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "mod13a2": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^mod13a2\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "mod13a3": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^mod13a3\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "mod13q1": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^mod13q1\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "myd09a1": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^myd09a1\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "myd09ga": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^myd09ga\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "myd09gq": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^myd09gq\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "myd09q1": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^myd09q1\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "myd13a1": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^myd13a1\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "myd13a2": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^myd13a2\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "myd13a3": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^myd13a3\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "myd13q1": {"properties": {"inputs": {"ItemCount": "inputs",
                                                          "items": {"pattern": "^myd13q1\\.a\\d{7}\\.h\\d{2}v\\d{2}\\.005\\.\\d{13}$",
                                                                     "type": "string"},
                                                          "minItems": 1,
                                                          "required": True,
                                                          "type": "array",
                                                          "uniqueItems": True},
                                              "products": {"items": {"enum": ["l1",
                                                                                 "stats"],
                                                                       "type": "string"},
                                                            "minItems": 1,
                                                            "required": True,
                                                            "restricted": True,
                                                            "stats": True,
                                                            "type": "array",
                                                            "uniqueItems": True}},
                              "type": "object"},
                 "note": {"blank": True,
                           "required": False,
                           "type": "string"},
                 "oli8": {"properties": {"inputs": {"ItemCount": "inputs",
                                                       "items": {"pattern": "^lo8\\d{3}\\d{3}\\d{4}\\d{3}\\w{3}.{2}$",
                                                                  "type": "string"},
                                                       "minItems": 1,
                                                       "required": True,
                                                       "type": "array",
                                                       "uniqueItems": True},
                                           "products": {"items": {"enum": ["source_metadata",
                                                                              "l1",
                                                                              "toa",
                                                                              "stats"],
                                                                    "type": "string"},
                                                         "minItems": 1,
                                                         "required": True,
                                                         "restricted": True,
                                                         "stats": True,
                                                         "type": "array",
                                                         "uniqueItems": True}},
                           "type": "object"},
                 "olitirs8": {"properties": {"inputs": {"ItemCount": "inputs",
                                                           "items": {"pattern": "^lc8\\d{3}\\d{3}\\d{4}\\d{3}\\w{3}.{2}$",
                                                                      "type": "string"},
                                                           "minItems": 1,
                                                           "required": True,
                                                           "type": "array",
                                                           "uniqueItems": True},
                                               "products": {"items": {"enum": ["source_metadata",
                                                                                  "l1",
                                                                                  "toa",
                                                                                  "bt",
                                                                                  "cloud",
                                                                                  "sr",
                                                                                  "sr_ndvi",
                                                                                  "sr_evi",
                                                                                  "sr_savi",
                                                                                  "sr_msavi",
                                                                                  "sr_ndmi",
                                                                                  "sr_nbr",
                                                                                  "sr_nbr2",
                                                                                  "stats",
                                                                                  "swe"],
                                                                        "type": "string"},
                                                             "minItems": 1,
                                                             "required": True,
                                                             "restricted": True,
                                                             "stats": True,
                                                             "type": "array",
                                                             "uniqueItems": True}},
                               "type": "object"},
                 "plot_statistics": {"type": "boolean"},
                 "projection": {"properties": {"aea": {"properties": {"central_meridian": {"maximum": 180,
                                                                                                "minimum": -180,
                                                                                                "required": True,
                                                                                                "type": "number"},
                                                                          "datum": {"enum": ["wgs84",
                                                                                               "nad27",
                                                                                               "nad83"],
                                                                                     "required": True,
                                                                                     "type": "string"},
                                                                          "false_easting": {"required": True,
                                                                                             "type": "number"},
                                                                          "false_northing": {"required": True,
                                                                                              "type": "number"},
                                                                          "latitude_of_origin": {"maximum": 90,
                                                                                                  "minimum": -90,
                                                                                                  "required": True,
                                                                                                  "type": "number"},
                                                                          "standard_parallel_1": {"maximum": 90,
                                                                                                   "minimum": -90,
                                                                                                   "required": True,
                                                                                                   "type": "number"},
                                                                          "standard_parallel_2": {"maximum": 90,
                                                                                                   "minimum": -90,
                                                                                                   "required": True,
                                                                                                   "type": "number"}},
                                                          "type": "object"},
                                                 "lonlat": {"type": "null"},
                                                 "ps": {"properties": {"false_easting": {"required": True,
                                                                                            "type": "number"},
                                                                         "false_northing": {"required": True,
                                                                                             "type": "number"},
                                                                         "latitude_true_scale": {"abs_rng": [60,
                                                                                                               90],
                                                                                                  "required": True,
                                                                                                  "type": "number"},
                                                                         "longitudinal_pole": {"maximum": 180,
                                                                                                "minimum": -180,
                                                                                                "required": True,
                                                                                                "type": "number"}},
                                                         "type": "object"},
                                                 "sin": {"properties": {"central_meridian": {"maximum": 180,
                                                                                                 "minimum": -180,
                                                                                                 "required": True,
                                                                                                 "type": "number"},
                                                                           "false_easting": {"required": True,
                                                                                              "type": "number"},
                                                                           "false_northing": {"required": True,
                                                                                               "type": "number"}},
                                                           "type": "object"},
                                                 "utm": {"properties": {"zone": {"maximum": 60,
                                                                                    "minimum": 1,
                                                                                    "required": True,
                                                                                    "type": "integer"},
                                                                          "zone_ns": {"enum": ["north",
                                                                                                 "south"],
                                                                                       "required": True,
                                                                                       "type": "string"}},
                                                          "type": "object"}},
                                 "single_obj": True,
                                 "type": "object"},
                 "resampling_method": {"enum": ["nn", "bil", "cc"],
                                        "type": "string"},
                 "resize": {"properties": {"pixel_size": {"ps_dd_rng": [0.0002695,
                                                                            0.0449155],
                                                             "ps_meter_rng": [30,
                                                                               5000],
                                                             "required": True,
                                                             "type": "number"},
                                             "pixel_size_units": {"enum": ["dd",
                                                                             "meters"],
                                                                   "required": True,
                                                                   "type": "string"}},
                             "type": "object"},
                 "tm4": {"properties": {"inputs": {"ItemCount": "inputs",
                                                      "items": {"pattern": "^lt4\\d{3}\\d{3}\\d{4}\\d{3}[a-z]{3}[a-z0-9]{2}$",
                                                                 "type": "string"},
                                                      "minItems": 1,
                                                      "required": True,
                                                      "type": "array",
                                                      "uniqueItems": True},
                                          "products": {"items": {"enum": ["source_metadata",
                                                                             "l1",
                                                                             "toa",
                                                                             "bt",
                                                                             "cloud",
                                                                             "sr",
                                                                             "swe",
                                                                             "sr_ndvi",
                                                                             "sr_evi",
                                                                             "sr_savi",
                                                                             "sr_msavi",
                                                                             "sr_ndmi",
                                                                             "sr_nbr",
                                                                             "sr_nbr2",
                                                                             "stats"],
                                                                   "type": "string"},
                                                        "minItems": 1,
                                                        "required": True,
                                                        "restricted": True,
                                                        "stats": True,
                                                        "type": "array",
                                                        "uniqueItems": True}},
                          "type": "object"},
                 "tm5": {"properties": {"inputs": {"ItemCount": "inputs",
                                                      "items": {"pattern": "^lt5\\d{3}\\d{3}\\d{4}\\d{3}[a-z]{3}[a-z0-9]{2}$",
                                                                 "type": "string"},
                                                      "minItems": 1,
                                                      "required": True,
                                                      "type": "array",
                                                      "uniqueItems": True},
                                          "products": {"items": {"enum": ["source_metadata",
                                                                             "l1",
                                                                             "toa",
                                                                             "bt",
                                                                             "cloud",
                                                                             "sr",
                                                                             "lst",
                                                                             "swe",
                                                                             "sr_ndvi",
                                                                             "sr_evi",
                                                                             "sr_savi",
                                                                             "sr_msavi",
                                                                             "sr_ndmi",
                                                                             "sr_nbr",
                                                                             "sr_nbr2",
                                                                             "stats"],
                                                                   "type": "string"},
                                                        "minItems": 1,
                                                        "required": True,
                                                        "restricted": True,
                                                        "stats": True,
                                                        "type": "array",
                                                        "uniqueItems": True}},
                          "type": "object"}},
 "set_ItemCount": ["inputs", 5000],
 "type": "object"}
```
