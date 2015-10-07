# espa-api
Demo API for the ESPA ordering system.

## Domain Description
The ESPA project (EROS Science Processing Architecture) is a system for producing advanced science products from existing products.  It operates on a scene by scene basis and is constructed to produce many products at once rather than a single product as quickly as possible (multiprocess vs multithreading).  Each product algorithm that runs only has access to the immediate observations spatial and temporal context, save any auxillary data needed such as ozone or water pressure measurements.

The system is composed of two major subsystems, ESPA ordering & scheduling and ESPA production.  

#### ESPA Ordering & Scheduling

The espa-api is meant to provide access to all espa ordering & scheduling operations in a standardized way

## Assumptions
1. The proposed API will be logically divided into a user api, system api and admin api.

2. All calls will be made over HTTPS only and will require HTTP Basic Authentication.
    * Users will be authenticated against the ERS (EROS Registration System).  Credentials used for EarthExplorer are used here.
    * The exception to this is the call to authenticate.  This call is needed so clients are able to determine if a user should even be allowed to perform operations.  This can later be modified to return roles.

3. Each operation will be stateless.  Sessions, cookies, etc will not be used.

4. Any payloads for POST or PUT operations will be valid JSON.  GET responses will also be JSON.


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


## Proposed Admin API Operations


###### Version 0 Demo (October 2015)
* Created to display url design for comment and review 
