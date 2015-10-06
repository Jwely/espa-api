# espa-api
Demo API for the ESPA ordering system.

## Assumptions
1. The proposed API will be logically divided into a user api, system api and admin api.

2. All calls will be made over HTTPS only and will require HTTP Basic Authentication.
    * Users will be authenticated against the ERS (EROS Registration System).  Credentials used for EarthExplorer are used here.

3. Each operation will be stateless.  Sessions, cookies, etc will not be used.


## Proposed User API Operations

```GET /api```
* List available versions

```GET /api/v0```
* Lists available operations

```GET /api/v0/user```
* Information for authenticated user
    * first name, last name, username, email, contactid

```GET /api/v0/orders```
* List all orders for the authenticated user

```GET /api/v0/orders/<email>```
* List all orders for the supplied email 

```GET /api/v0/order/<ordernum>```
* Retrieve details for the supplied order.

```POST /api/v0/order/check```
* Returns available processing for supplied items.  Needed to build intelligent clients.

```POST /api/v0/order```
* Enter a new order 


## Proposed System API Operations


## Proposed Admin API Operations


###### Version 0 Demo (October 2015)
* Created to display url design for comment and review 
