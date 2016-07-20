## User API
The User API is intended to be outward facing and available for anyone to code and interact with.  Version 0 provides the minimum functionality necessary to place orders, view orders, determine available products from a list of inputs and determine available projections with their associated parameters/value ranges.

Additional functionality may be added in later releases.  Some of these items include allowing users to search rather than requiring a scene list as input, allowing users to search and/or clip to predefined grid & tile extents (example: find all scenes that have data in the extents defined by WELD CONUS Tile h01v03 where cloud cover is less than x% and the observation month is June, July or August), or caching/identifying ESPA outputs that could be reused in another order.

Users may also want to specify an output file naming scheme that could be provided via templating and captured at order submission time.  None of these items are addressed in version 0.

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
        "/api/v0/request/<ordernum>": {
            "function": "retrieve order sent to server",
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
**GET /api/v0/order/\<ordernum\>**

Retrieves a submitted order. Some information may be omitted from this response depending on access privileges.
```json
curl --user username:password https://espa.cr.usgs.gov/api/v0/order/production@usgs.gov-03072016-081013
{
  "completion_date": "Mon, 07 Mar 2016 08:11:01 GMT",
  "note": "",
  "order_date": "Mon, 07 Mar 2016 08:10:13 GMT",
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

**POST /api/v0/order**

Accepts requests for process from an HTTP POST with a JSON body.  The body is validated and any errors are returned to the caller.  Otherwise, an orderid is returned.
```json

curl --user username:password -d '{"olitirs8": {
                                                    "inputs": ["LC8027029201533LGN00"], 
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
                                                    }
                                     "image_extents": {
                                                        "north": 0.0002695,
                                                        "south": 0,
                                                        "east": 0.0002695,
                                                        "west": 0,
                                                        "units": "dd"
                                                    }
                                     }' https://espa.cr.usgs.gov/api/v0/order

Returns:
{
    "orderid": "production@email.com-101015143201-00132"
}
```
