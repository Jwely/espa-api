## User API
The User API is intended to be outward facing and available for anyone to code and interact with.  Version 0 provides the minimum functionality necessary to place orders, view orders, determine available products from a list of inputs and determine available projections with their associated parameters/value ranges.

Additional functionality may be added in later releases.  Some of these items include allowing users to search rather than requiring a scene list as input, allowing users to search and/or clip to predefined grid & tile extents (example: find all scenes that have data in the extents defined by WELD CONUS Tile h01v03 where cloud cover is less than x% and the observation month is June, July or August), or caching/identifying ESPA outputs that could be reused in another order.

Users may also want to specify an output file naming scheme that could be provided via templating and captured at order submission time.  None of these items are addressed in version 0.

### User API Operations

```GET /api```
```json
curl http://localhost:5000/api

{
  "version_0": {
    "description": "Demo URLS for development",
    "url": "/api/v0"
  }
}
```

```GET /api/v0```
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

```POST /api/v0/authenticate```

```json
curl -d '{"username":"production", "password":"password"}' http://localhost:5000/api/v0/authenticate

{
  "result": true
}
```

```GET /api/v0/user```

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
   
```GET /api/v0/available-products/<product_id>```
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

```POST /api/v0/available-products```
```json
curl --user production:password 
-d '{"inputs":["LE70290302003123EDC00", "MOD09A1.A2000073.h12v11.005.2008238080250.hdf", "bad scene id"]}' http://localhost:5000/api/v0/available-products

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
}```

```GET /api/v0/projections```
* Returns available projections

```GET /api/v0/projections/<projection>```
* Returns required projection parameters and ranges

```GET /api/v0/orders```
```json
curl --user production:password http://localhost:5000/api/v0/orders

{
  "orders": [
    "processing@email.com-101015143201-00132",
    "processing@email.com-101115143201-00132"
  ]
}
```

```GET /api/v0/orders/<email>```
* List all orders for the supplied email 

```GET /api/v0/order/<ordernum>```
* Retrieve details for the supplied order.

```POST /api/v0/order/validate```
* Validates a user order.  Can be used prior to POST'ing an order (same logic will be applied during order submission)

```POST /api/v0/order```
* Enter a new order, accepts a populated template as returned from /api/v0/order/template

## Production API
The Production API is intended to be used by the system or systems that are fulfilling the end user production requests.  As such, the API simply allows production systems to retrieve items to process and then update their status.  There is also a method for retrieving configuration data.

### Production API Operations
```GET /production-api```
* List available versions

```GET /production-api/v0```
* List available operations

```GET /production-api/v0/products?priority=['high'|'normal'|'low']&user='username'&sensor=['modis'|'landsat'|'plot']```
* Returns products ready for production

```PUT /production-api/v0/<orderid>/<productid>```
* Update product status, completed file locations, etc

```GET /production-api/v0/configuration/<key>```
* Lists information for specified configuration key  

* _possibly more to define_

## Admin API
The admin API encompasses everything needed for day-to-day operation & maintenance of the system.  Ops staff will be able to start & stop each part of the system as necessary, manipulate the data stored on the distribution cache, view & manipulate user orders & products, etc.

### Admin API Operations
```GET /admin-api```
* List available versions

```GET /admin-api/v0```
* List available operations
* 

``` GET /admin-api/v0/user?limit=<limit>&orderby=<orderbyfields>&email=<email>&username=<username>```
* List users + their info

``` GET /admin-api/v0/orders```
* Overview of orders & their status, order age, etc.

```GET /admin-api/v0/orders?limit=#&order_by=<fieldname>&user=<username>&email=<email>&start_date=<date>&end_date=<date>```
* Overview of order information

```PUT /admin-api/v0/order/cancel/<orderid>```
* Cancels an order.  Admin only for now, later should be offered through the User API as well.
  * requires stopping hadoop jobs, deleting files from the cache and resetting the db status for all the other scenes that weren't cancelled but were grouped into the same jobs

```GET /admin-api/v0/products```
* Overview of product information & status, # of products per status

```GET /admin-api/v0/products?hadoop_job=<jobid>&status=<status>&processing_location=<location>&completed_date=<date>&user=<username>&email=<email>```
* List products that meet the specified criteria

```PUT /admin-api/v0/products/resubmit```
* Resubmits the products supplied in the body

#### General configuration items
```GET /admin-api/v0/configuration```
* Lists all configuration keys & values

```GET /admin-api/v0/configuration/<key>```
* Lists information for specified key 

```POST /admin-api/v0/configuration/<key>```
* Add new configuration item
 
```PUT /admin-api/v0/configuration/<key>```
* Update existing configuration item

```DELETE /admin-api/v0/configuration/<key>```

#### Hadoop specific items
```GET /admin-api/v0/hadoop/jobs```
* List Hadoop jobs

```DELETE /admin-api/v0/hadoop/jobs/<jobid>```
* Kill Hadoop job

#### System related operations
```GET /admin-api/v0/system/status```
* Status of full processing system, on/off

```PUT /admin-api/v0/system/disposition/<on|off>```
* Switch order disposition subsystem on or off

```PUT /admin-api/v0/system/load_external_orders/<on|off>```
* Switch external order loading subsystem on or off

```PUT /admin-api/v0/system/production/<on|off>```
* Switch production subsystem on or off

```PUT /admin-api/v0/system/hadoop/<on|off>```
* Startup/shutdown Hadoop

```PUT /admin-api/v0/system/website/<on|off>```
* Allow normal order access or block access with system maintenance page

#### Online cache operations
```GET /admin-api/v0/onlinecache/stats```
* Return usage stats for disk

```GET /admin-api/v0/onlinecache/list```
* List all orders on disk
 
```GET /admin-api/v0/onlinecache/list/<orderid>```
* List files for orderid

```DELETE /admin-api/v0/onlinecache/<orderid>```
* Delete an order from disk

```DELETE /admin-api/v0/onlinecache/<orderid>/<filename>```
* Delete a file from disk for a specific order

* _possibly more to define_

