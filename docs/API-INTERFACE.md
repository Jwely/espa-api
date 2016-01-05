## User API
The User API is intended to be outward facing and available for anyone to code and interact with.  Version 0 provides the minimum functionality necessary to place orders, view orders, determine available products from a list of inputs and determine available projections with their associated parameters/value ranges.

Additional functionality may be added in later releases.  Some of these items include allowing users to search rather than requiring a scene list as input, allowing users to search and/or clip to predefined grid & tile extents (example: find all scenes that have data in the extents defined by WELD CONUS Tile h01v03 where cloud cover is less than x% and the observation month is June, July or August), or caching/identifying ESPA outputs that could be reused in another order.

Users may also want to specify an output file naming scheme that could be provided via templating and captured at order submission time.  None of these items are addressed in version 0.

### User API Operations

**GET /api**

Lists all available versions of the api.
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

Lists all available api operations.
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

Authenticates the username + password.  This wouldn't be necessary if the web tier were authenticating with EE via the encrypted cookie.  
```json
curl -d '{"username":"production", "password":"password"}' 
http://localhost:5000/api/v0/authenticate

{
  "result": true
}
```

**GET /api/v0/user**

Returns user information for the authenticated user.
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

Lists the available output products for the supplied input.
```json
curl --user production:password 
http://localhost:5000/api/v0/available-products/LE70290302003123EDC00

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

Lists available products for the supplied inputs.  Also classifies the inputs by sensor or lists as 'not implemented' if the values cannot be ordered or determined.
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

Lists and describes available projections.  This is a dump of the schema defined that constrains projection info.
```json
curl --user production:password 
http://localhost:5000/api/v0/available-products/LE70290302003123EDC00

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

Lists all available output formats
```json
curl --user production:password 
http://localhost:5000/api/v0/available-products/LE70290302003123EDC00

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

List orders for the authenticated user.
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

Lists orders for the supplied email.  Necessary to support user collaboration.
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

Retrieves a submitted order. Some information may be omitted from this response depending on access privileges.
```json
curl --user production:password 
http://localhost:5000/api/v0/order/production@email.com-101015143201-00132

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

Accepts requests for process from an HTTP POST with a JSON body.  The body is validated and any errors are returned to the caller.  Otherwise, an orderid is returned.
```json
curl --user production:password -d '{"inputs":["LE70290302003123EDC00", "LT50290302002123EDC00"], 
                                     "products":["etm_sr", "tm_sr", "stats"],
                                     "projection": {
                                         "name": "aea",
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
```

**GET /api/v0/order**
This is an alternative option for ordering.  I would appreciate hearing what YOUR preferred method would be if I could only implement one.

Accepts a request for production from an HTTP GET.  Either returns the url the completed product can be downloaded from if complete or returns an orderid for the item.  This call should be indempotent and would therefore support reusing already processed items.

There are several advantages to moving to this style of operation.  
1. It is simple and eliminates unnecessary complexity  
2. It is testable and usable directly from a browser.
3. It forces a many-to-many structure for orders to scenes/products, enabling reuse of the cache (ESPA currently has a very high cache hit rate but is not set up to take advantage of it.  This means saving real dollars as less disk cache will be necessary to scale).  
4. We can be more responsive to end users.  They would obtain data faster if the scenes were already on cache.  We would have to process less.  We would allow most items to remain on the cache much longer, and they would only be purged as they lost popularity to other items.  
5. For end users, this is as easy as it gets.  Hit a url.  You either get a download url or an orderid.  Instead of an orderid maybe we could even just provide information about the item and where it's at in the processing queue.  (submitted on this date, has this many items ahead of it, etc).

There are several disadvantages:
1. ESPA is not set up to operate on an item by item basis.  Orders are a real thing (many-to-one) so we'd have to do the engineering and migrate to the new way of operating. 
2. It makes the cache purge a bit more complex, but not by much.
3. It would be require statistical plotting to be reworked.
4. Tracking down issues with user orders would be _different_.  That is, harder or easier depending on what the issue is.  Seeing the users entire order on disk would be more complex.  Tracking down individual items would be far simpler.

This is currently describing the service as returning a download url if the item is available.  I would LOVE to take this further and have the file actually start downloading if it's available instead, thus getting us down to a single, authoritative url for a given product in our system.  This would require significant rework and scaling at the app tier level as it's only hooked up to 1Gb line and is also a single instance.  It *is* the right thing to do, however.

This should also leverage previously processed base images when a user is requesting customization.  For example, if a user requests subsets from an SR product, we should go look to see if there is already the SR base image out there on disk and if there is, ingest that and just subset it then redeliver.  The way it works today is everything is rerun from scratch.  So the question is, is this an operational system now and if so, should we be acting like it is?

```json
curl --user production:password http://localhost:5000/api/v0/order
?input=LE70290302003123EDC00&products=etm_sr,etm_toa&projection=aea
&standard_parallel_1=29.5&standard_parallel_2=45.5
&latitude_of_origin=23.0&false_easting=0.0&false_northing=0.0
&north=3164800&south=3014800
&east=-2415600&west=-2565600
&format=gtiff&pixel_size=60
&pixel_size_units=meters&resampling_method=nn

or shortened:

curl --user production:password http://localhost:5000/api/v0/order
?i=LE70290302003123EDC00&o=etm_sr,etm_toa
&p=aea
&psp1=29.5&psp2=45.5
&plo=23.0&pfe=0.0&pfn=0.0
&en=3164800&es=3014800
&ee=-2415600&ew=-2565600
&fmt=gtiff&pxs=60
&pxsu=m&rm=nn

{
    "orderid": "production@email.com-101015143201-00132"
}

or

{
    "url": "http://localhost:5000/downloads/LE70290302003123-SC20151101.tar.gz"
}
```

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

