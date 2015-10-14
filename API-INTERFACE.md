## User API Operations

```GET /api```
* List available versions

```GET /api/v0```
* Lists available operations

```POST /api/v0/authenticate```
* Accepts a username/password and returns True/False.  Needed to support client development.

```GET /api/v0/user```
* Information for authenticated user
    * first name, last name, username, email, contactid

```GET /api/v0/orders```
* List all orders for the authenticated user

```GET /api/v0/orders/<email>```
* List all orders for the supplied email 

```GET /api/v0/order/<ordernum>```
* Retrieve details for the supplied order.

```POST /api/v0/order/template```
* Returns order template for supplied items.  Needed to build intelligent clients.

```POST /api/v0/order```
* Enter a new order, accepts a populated template as returned from /api/v0/order/template

```GET /api/v0/projections```
* Returns available projections

```GET /api/v0/projections/<projection>```
* Returns required projection parameters and ranges


## Production API Operations
```GET /production-api/v0/products?priority=['high'|'normal'|'low']&user='username'&sensor=['modis'|'landsat'|'plot']```
* Returns products ready for production

```PUT /production-api/v0/<orderid>/<productid>```
* Update product status, completed file locations, etc

```GET /production-api/v0/configuration/<key>```
* Lists information for specified configuration key  

* _possibly more to define_

## Admin API Operations
``` GET /admin-api/v0/user?limit=<limit>&orderby=<orderbyfields>&email=<email>&username=<username>```
* List users + their info

``` GET /admin-api/v0/orders```
* Overview of orders & their status, order age, etc.

```GET /admin-api/v0/orders?limit=#&order_by=<fieldname>&user=<username>&email=<email>&start_date=<date>&end_date=<date>```
* Overview of order information

```PUT /admin-api/v0/order/cancel/<orderid>```
* Cancels an order

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
```GET /admin-api/v0/system```
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

* _possibly more to define_

