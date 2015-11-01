## User API
The User API is intended to be outward facing and available for anyone to code and interact with.  Version 0 provides the minimum functionality necessary to place orders, view orders, determine available products from a list of inputs and determine available projections with their associated parameters/value ranges.

Additional functionality may be added in later releases.  Some of these items include allowing users to search rather than requiring a scene list as input, allowing users to search and/or clip to predefined grid & tile extents (example: find all scenes that have data in the extents defined by WELD CONUS Tile h01v03 where cloud cover is less than x% and the observation month is June, July or August), or caching/identifying ESPA outputs that could be reused in another order.

Users may also want to specify an output file naming scheme that could be provided via templating and captured at order submission time.  None of these items are addressed in version 0.

### User API Operations

**GET /api**
```json
curl http://localhost:5000/api

{
  "version_0": {
    "description": "Demo URLS for development",
    "url": "/api/v0"
  }
}
```

**GET /api/v0**
```json
curl http://localhost:5000/api/v0

{
  "/api": {
    "endpoint": "list_versions",
    "methods": [
      "HEAD",
      "OPTIONS",
      "GET"
    ]
  },
  "/api/v0": {
    "endpoint": "list_operations",
    "methods": [
      "HEAD",
      "OPTIONS",
      "GET"
    ]
  },
  "/api/v0/authenticate": {
    "endpoint": "authenticate",
    "methods": [
      "POST",
      "OPTIONS"
    ]
  },
  "/api/v0/user": {
    "endpoint": "user_info",
    "methods": [
      "HEAD",
      "OPTIONS",
      "GET"
    ]
  }
}
```

**POST /api/v0/authenticate**

```json
curl -d '{"username":"production", "password":"password"}' http://localhost:5000/api/v0/authenticate

{
  "result": true
}
```

**GET /api/v0/user**

```json
curl --user production:password http://localhost:5000/api/v0/user

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
```json
curl --user production:password http://localhost:5000/api/v0/available-products/LE70290302003123EDC00

{
  "etm": {
    "inputs": [
      "LE70290302003123EDC00"
    ],
    "outputs": [
      "etm_sr",
      "etm_toa",
      "etm_l1",
      "etm_sr_ndvi",
      "etm_sr_ndmi",
      "etm_sr_evi",
      "etm_sr_savi",
      "etm_sr_msavi",
      "etm_sr_nbr",
      "etm_sr_nbr2",
      "source",
      "source_metadata"
    ]
  }
}
```

**POST /api/v0/available-products**
```json
curl --user production:password 
-d '{"inputs":["LE70290302003123EDC00",
               "MOD09A1.A2000073.h12v11.005.2008238080250.hdf",
               "bad scene id"]}'
http://localhost:5000/api/v0/available-products

{
  "etm": {
    "inputs": [
      "LE70290302003123EDC00"
    ],
    "outputs": [
      "etm_sr",
      "etm_toa",
      "etm_l1",
      "etm_sr_ndvi",
      "etm_sr_ndmi",
      "etm_sr_evi",
      "etm_sr_savi",
      "etm_sr_msavi",
      "etm_sr_nbr",
      "etm_sr_nbr2",
      "source",
      "source_metadata"
    ]
  },
  "not_implemented": [
    "bad scene id"
  ],
  "terra": {
    "inputs": [
      "MOD09A1.A2000073.h12v11.005.2008238080250.hdf"
    ],
    "outputs": [
      "mod_l1",
      "source",
      "source_metadata"
    ]
  }
}
```

**GET /api/v0/projections**
```json
curl --user production:password http://localhost:5000/api/v0/available-products/LE70290302003123EDC00

{
  "aea": {
    "central_meridian": {
      "max": 180.0, 
      "min": -180.0, 
      "required": true, 
      "type": "float"
    }, 
    "false_easting": {
      "required": true, 
      "type": "float"
    }, 
    "false_northing": {
      "required": true, 
      "type": "float"
    }, 
    "latitude_of_origin": {
      "max": 90.0, 
      "min": -90.0, 
      "required": true, 
      "type": "float"
    }, 
    "name": {
      "allowed": [
        "aea"
      ], 
      "required": true, 
      "type": "string"
    }, 
    "standard_parallel_1": {
      "max": 90.0, 
      "min": -90.0, 
      "required": true, 
      "type": "float"
    }, 
    "standard_parallel_2": {
      "max": 90.0, 
      "min": -90.0, 
      "required": true, 
      "type": "float"
    }
  }, 
  "lonlat": {
    "name": {
      "allowed": [
        "lonlat"
      ], 
      "required": true, 
      "type": "string"
    }
  }, 
  "ps": {
    "latitude_true_scale": {
      "anyof": [
        {
          "max": -60.0, 
          "min": -90.0
        }, 
        {
          "max": 90.0, 
          "min": 60.0
        }
      ], 
      "required": true, 
      "type": "float"
    }, 
    "longitudinal_pole": {
      "max": 180.0, 
      "min": -180.0, 
      "required": true, 
      "type": "float"
    }, 
    "name": {
      "allowed": [
        "ps"
      ], 
      "required": true, 
      "type": "string"
    }
  }, 
  "sinu": {
    "central_meridian": {
      "max": 180.0, 
      "min": -180.0, 
      "required": true, 
      "type": "float"
    }, 
    "false_easting": {
      "required": true, 
      "type": "float"
    }, 
    "false_northing": {
      "required": true, 
      "type": "float"
    }, 
    "name": {
      "allowed": [
        "sinu"
      ], 
      "required": true, 
      "type": "string"
    }
  }, 
  "utm": {
    "name": {
      "allowed": [
        "utm"
      ], 
      "required": true, 
      "type": "string"
    }, 
    "zone": {
      "max": 60, 
      "min": 1, 
      "required": true, 
      "type": "integer"
    }, 
    "zone_ns": {
      "allowed": [
        "north", 
        "south"
      ], 
      "required": true, 
      "type": "string"
    }
  }
}
```
**GET /api/v0/formats**
```json
curl --user production:password http://localhost:5000/api/v0/available-products/LE70290302003123EDC00

{
  "formats": [
    "gtiff", 
    "hdf-eos2", 
    "envi"
  ]
}
```

**GET /api/v0/resampling-methods**
```json
curl --user production:password http://localhost:5000/api/v0/resampling-methods

{
  "resampling_methods": [
    "nn", 
    "bil", 
    "cc"
  ]
}
```

**GET /api/v0/orders**
```json
curl --user production:password http://localhost:5000/api/v0/orders

{
  "orders": [
    "production@email.com-101015143201-00132", 
    "production@email.com-101115143201-00132"
  ]
}
```

**GET /api/v0/orders/\<email\>**
```json
curl --user production:password http://localhost:5000/api/v0/orders/production@email.com

{
  "orders": [
    "production@email.com-101015143201-00132", 
    "production@email.com-101115143201-00132"
  ]
}
```
**GET /api/v0/order/\<ordernum\>**
```json
curl --user production:password http://localhost:5000/api/v0/order/production@email.com-101015143201-00132

{
  "completion_date": "", 
  "completion_email_sent": "", 
  "customization": {
    "extents": {
      "east": -2415600, 
      "north": 3164800, 
      "south": 3014800, 
      "west": -2565600
    }, 
    "format": "gtiff", 
    "projection": {
      "central_meridian": -96.0, 
      "code": "aea", 
      "false_easting": 0.0, 
      "false_northing": 0.0, 
      "latitude_of_origin": 23.0, 
      "standard_parallel_1": 29.5, 
      "standard_parallel_2": 45.5
    }, 
    "resize": {
      "pixel_size": 30, 
      "pixel_size_units": "meters"
    }
  }, 
  "ee_order_id": "", 
  "initial_email_sent": "2015-10-10", 
  "inputs": {
    "LT50290302002123EDC00": {
      "completion_date": "2015-10-12", 
      "download_url": "http://localhost:5000/orders/order1/LT50290302002123EDC00.tar.gz", 
      "status": "complete"
    }, 
    "LT50300302002123EDC00": {
      "hadoop_job_id": "job_abc123", 
      "processing_location": "processingNode1", 
      "status": "processing"
    }, 
    "LT50310302002123EDC00": {
      "completion_date": null, 
      "status": "oncache"
    }
  }, 
  "note": "", 
  "order_date": "2015-10-10", 
  "order_source": "bulk api", 
  "order_type": "ondemand", 
  "priority": "high", 
  "products": [
    "tm_sr", 
    "tm_sr_ndvi", 
    "tm_toa"
  ], 
  "status": "ordered"
}

```
**GET /api/v0/order/request/\<ordernum\>**
* Retrieve the order that was sent to the server.  Resubmittable to the order endpoint.
  * don't know if we need this or not 


**POST /api/v0/order**
```json
curl --user production:password -d '{"inputs":["LE70290302003123EDC00", "LT50290302002123EDC00"], 
                                     "products":["etm_sr", "tm_sr", "stats"],
                                     "projection": {
                                         "name": "aea"
                                         "standard_parallel_1": 29.5,
                                         "standard_parallel_2": 45.5,
                                         "central_meridian": -96.0,
                                         "latitude_of_origin": 23.0,
                                         "false_easting": 0.0,
                                         "false_northing": 0.0,
                                     },
                                     "image_extents": {
                                         "north": 3164800,
                                         "south": 3014800,
                                         "east": -2415600,
                                         "west": -2565600
                                     }, 
                                     "format": "gtiff",
                                     "resize": {
                                         "pixel_size": 60,
                                         "pixel_size_units": "meters"
                                     },
                                     "resampling_method": "nn"
                                    }'
      http://localhost:5000/api/v0/order

{
    "orderid": "production@email.com-101015143201-00132"
}

## Production API
The Production API is intended to be used by the system or systems that are fulfilling the end user production requests.  As such, the API simply allows production systems to retrieve items to process and then update their status.  There is also a method for retrieving configuration data.

### Production API Operations
**GET /production-api**
* List available versions

**GET /production-api/v0**
* List available operations

**GET /production-api/v0/products?priority=['high'|'normal'|'low']&user='username'&sensor=['modis'|'landsat'|'plot']**
* Returns products ready for production

**PUT /production-api/v0/\<orderid\>/\<productid\>**
* Update product status, completed file locations, etc

**GET /production-api/v0/configuration/\<key\>**
* Lists information for specified configuration key  

* _possibly more to define_

## Admin API
The admin API encompasses everything needed for day-to-day operation & maintenance of the system.  Ops staff will be able to start & stop each part of the system as necessary, manipulate the data stored on the distribution cache, view & manipulate user orders & products, etc.

### Admin API Operations
**GET /admin-api**
* List available versions

**GET /admin-api/v0**
* List available operations
* 

**GET /admin-api/v0/user?limit=\<limit\>&orderby=\<orderbyfields\>&email=\<email\>&username=\<username\>**
* List users + their info

**GET /admin-api/v0/orders**
* Overview of orders & their status, order age, etc.

**GET /admin-api/v0/orders?limit=#&order_by=\<fieldname\>&user=\<username\>&email=\<email\>&start_date=\<date\>&end_date=\<date\>**
* Overview of order information

**PUT /admin-api/v0/order/cancel/\<orderid\>**
* Cancels an order.  Admin only for now, later should be offered through the User API as well.
  * requires stopping hadoop jobs, deleting files from the cache and resetting the db status for all the other scenes that weren't cancelled but were grouped into the same jobs

**GET /admin-api/v0/products**
* Overview of product information & status, # of products per status

**GET /admin-api/v0/products?hadoop_job=\<jobid\>&status=\<status\>&processing_location=\<location\>&completed_date=\<date\>&user=\<username\>&email=\<email\>**
* List products that meet the specified criteria

**PUT /admin-api/v0/products/resubmit**
* Resubmits the products supplied in the body

#### General configuration items
**GET /admin-api/v0/configuration**
* Lists all configuration keys & values

**GET /admin-api/v0/configuration/\<key\>**
* Lists information for specified key 

**POST /admin-api/v0/configuration/\<key\>**
* Add new configuration item
 
**PUT /admin-api/v0/configuration/\<key\>**
* Update existing configuration item

**DELETE /admin-api/v0/configuration/\<key\>**

#### Hadoop specific items
**GET /admin-api/v0/hadoop/jobs**
* List Hadoop jobs

**DELETE /admin-api/v0/hadoop/jobs/\<jobid\>**
* Kill Hadoop job

#### System related operations
**GET /admin-api/v0/system/status**
* Status of full processing system, on/off

**PUT /admin-api/v0/system/disposition/\<on|off\>**
* Switch order disposition subsystem on or off

**PUT /admin-api/v0/system/load_external_orders/\<on|off\>**
* Switch external order loading subsystem on or off

**PUT /admin-api/v0/system/production/\<on|off\>**
* Switch production subsystem on or off

**PUT /admin-api/v0/system/hadoop/\<on|off\>**
* Startup/shutdown Hadoop

**PUT /admin-api/v0/system/website/\<on|off\>**
* Allow normal order access or block access with system maintenance page

#### Online cache operations
**GET /admin-api/v0/onlinecache/stats**
* Return usage stats for disk

**GET /admin-api/v0/onlinecache/list**
* List all orders on disk
 
**GET /admin-api/v0/onlinecache/list/\<orderid\>**
* List files for orderid

**DELETE /admin-api/v0/onlinecache/\<orderid\>**
* Delete an order from disk

**DELETE /admin-api/v0/onlinecache/\<orderid\>/\<filename\>**
* Delete a file from disk for a specific order

* _possibly more to define_

