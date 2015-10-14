## Proposed User API Operations

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



## Proposed System API Operations
```GET /system-api/v0/products?priority=['high'|'normal'|'low']&user='username'&sensor=['modis'|'landsat'|'plot']```
* Returns products ready for production

```PUT /system-api/v0/<orderid>/<productid>```
* Update product status, completed file locations, etc

* possibly more to define

## Proposed Admin API Operations
```GET /admin-api/v0/orders?limit=#&order_by=fieldname&user=username&start_date=date&end_date=date```
* Overview of order information
 
```GET /admin-api/v0/products```
* Overview of product information & status, # of products per status
 
* more to define

