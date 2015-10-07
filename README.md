# espa-api
Demo API for the ESPA ordering & scheduling system.

## Overview
The ESPA project (EROS Science Processing Architecture) is a system for producing advanced science products from existing products. It was originally constructed to serve as a production platform for science algorithms under incubation but has since transitioned into a quasi-operational state within USGS EROS, due primarily to the popularity of it's products.

ESPA operates on a scene by scene basis and was built to produce many products at once rather than a single product as quickly as possible (multiprocess vs multithreading).  Each product algorithm execution only has access to the spatial and temporal context of the observation in question, save any auxillary data needed such as ozone or water pressure measurements.  ESPA is therefore highly optimized for single-scene (observation) but is wholly unsuited for compositing, mosaicing, or time-series analysis, or any other operation that requires information from a separate observation.

The system is composed of two major subsystems, espa-web and espa-production.

#### espa-web
espa-web provides all the ordering & scheduling operations for the system, as well as the majority of the integration with the rest of USGS EROS ordering systems.  This means that espa-web knows how to capture user orders, validate parameters, determine order + product disposition (including placing & monitoring orders for level 1 data), notifying users of completed orders and providing access to download completed products.  It also provides services for espa-production to retrieve production requests and to capture production status updates.

espa-web currently captures user orders from two sources: The espa.cr.usgs.gov website itself and also USGS Earth Explorer.  Orders are obtained from USGS EE via web services hosted by the Long Term Archive (LTA) project.

#### espa-production
espa-production is responsible for receiving production requests, validating the requests, locating and using any necessary auxillary data, transferring level 1 data to a working directory, executing the necessary science algorithms to produce the product, placing the finished product in a distribution location and finally notifying espa-web that the production request is complete.  espa-production is a stateless system, with each production run remaining isolated from any other.

## Why create an API?
As previously discussed above, the original system was built solely as a temporary incubation platform for science products.  The only original requirement was to produce 450 surface refectance (SR) corrections to level 1 data per day and make the outputs available to end users, and to (obviously) accomplish this work as quickly and cheaply as possible.  For context, ESPA now is capable of performing over 23,000 SR corrections per day (as of October 2015).  The capacity increases have been driven purely by demand.

New requirements have emerged from the science community that detail the need to perform deep time series analysis against atmospherically corrected observations.  This body of work is being accompished as part of the Land Change Monitoring Assessment and Prediction (LCMAP) project.  LCMAP requires (or will in the near future) the full Landsat archive corrected to surface reflectance, first for the continental United States & Alaska, and later globally.  It also requires any new observations to be corrected so they can be incorporated into it's output products.

ESPA currently provides access to order data via web interfaces only. (espa.cr.usgs.gov and earthexplorer.usgs.gov).  This is clearly inadequate to establish an automated pipeline for ongoing analysis: No human wants to manually order, track and transfer millions of scenes. The ESPA system must be modified to provide an application programming interface for downstream systems to gain access to its capabilities.

## Domain Entities, Constraints and Rules
1.  The system captures a user supplied list of input observations, desired output products and customizations and groups this as an order.
    1. The user supplied list of input observations is a newline `\n` separated file with each line containing a Landsat scene id or MODIS tile id.  Landsat Thematic Mapper (TM), Enhanced Thematic Mapper + (ETM+), Operational Land Imager (OLI) ,Operational Land Imager/Thermal Infrared Sensor(OLI/TIRS), MODIS 09A1, MODIS 09GA, MODIS 09GQ, MODIS 09Q1, MODIS 13A1, MODIS 13A2, MODIS 13A3 and MODIS 13Q1 products may be supplied as inputs.
2. The available output product list varies with each input type.
    1. Example: OLI & MODIS products cannot be corrected to surface reflectance.  OLI cannot due to not having thermal data available for cloud detection.  MODIS cannot as MODIS 09 products are _already_ at surface reflectance and MODIS 13 products are merely a vegetation index.
3. The available output products list varies within each input type.
    1. Example: Not all Landsat TM/ETM+/OLITIRS scenes can be corrected to surface reflectance, particularly nighttime observations.
4. The available output product list varies based on the spatial and temporal characterics of the input observations.
    1. Example: Land Surface Temperature cannot currently be produced outside of certain geographic extents due to insufficient auxillary data.
5. Requests for output customization are captured at the order (not the input observation) level.  These customizations are applied against every ESPA output product in the order.
    1. Users may request that their order is reprojected to sinusoidal, albers, UTM, geographic or polar stereographic.  Each projection requires its own set of parameters which must be validated.
    2. Users may request their order is output in binary (envi), HDF EOS2, or GeoTiFF format.
    3. Users may request modification of the spatial output extents (spatial subsetting) of all output products in either projection coordinates or decimal degrees.
    4. Users may request pixel resizing of the output products in either meters or decimal degrees.
    5. Where necessary, users may choose their desired resampling method.

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
