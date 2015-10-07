# espa-api
Demo API for the ESPA ordering & scheduling system.

## Domain Description
The ESPA project (EROS Science Processing Architecture) is a system for producing advanced science products from existing products. It was originally constructed to serve as a production platform for science algorithms under incubation but has since transitioned into a quasi-operational state within USGS EROS, due primarily to the popularity of it's products.

ESPA operates on a scene by scene basis and was built to produce many products at once rather than a single product as quickly as possible (multiprocess vs multithreading).  Each product algorithm execution only has access to the spatial and temporal context of the observation in question, save any auxillary data needed such as ozone or water pressure measurements.  ESPA is therefore highly optimized for single-scene (observation) but is wholly unsuited for compositing, mosaicing, or time-series analysis, or any other operation that requires information from a separate observation.

The system is composed of two major subsystems, espa-web and espa-production.

#### espa-web
espa-web provides all the ordering & scheduling operations for the system, as well as the majority of the integration with the rest of USGS EROS ordering systems.  This means that espa-web knows how to capture user orders, validate parameters, determine order + product disposition (including placing & monitoring orders for level 1 data), notifying users of completed orders and providing access to download completed products.  It also provides services for espa-production to retrieve production requests and to capture production status updates.

espa-web currently captures user orders from two sources: The espa.cr.usgs.gov website itself and also USGS Earth Explorer.  Orders are obtained from USGS EE via web services hosted by the Long Term Archive (LTA) project.

#### espa-production
espa-production is responsible for receiving production requests, validating the requests, locating and using any necessary auxillary data, transferring level 1 data to a working directory, executing the necessary science algorithms to produce the product, placing the finished product in a distribution location and finally notifying espa-web that the production request is complete.  espa-production is a stateless system, with each production run remaining isolated from any other.

## Assumptions
1. The proposed API will be logically divided into a user API, system API and admin API.  
    * The user api will accept orders and provide end user access to order/product status and links to download completed products.
    * The system API serves functionality to espa-production, mainly for obtaining production requests and capturing production status.  
    * The admin API will allow operations & maintenance staff to monitor and manipulate the system as needed.

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
