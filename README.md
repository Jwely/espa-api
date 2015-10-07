# espa-api
Demo API for the ESPA ordering & scheduling system.

## Overview
The ESPA project is a system for producing advanced science products from existing products. It was originally constructed to serve as a production platform for science algorithms under incubation but has since transitioned into a quasi-operational state within USGS EROS, due primarily to the popularity of it's products.

ESPA operates on a scene by scene basis and was built to produce many products at once rather than a single product as quickly as possible (multiprocess vs multithreading).  Each product algorithm execution only has access to the spatial and temporal context of the observation in question, save any auxillary data needed such as ozone or water pressure measurements.  ESPA is therefore highly optimized for single-scene (observation) but is wholly unsuited for compositing, mosaicing, or time-series analysis, or any other operation that requires information from a separate observation.

The system is composed of two major subsystems, espa-web and espa-production.

#### espa-web
espa-web provides all the ordering & scheduling operations for the system, as well as the majority of the integration with the rest of USGS EROS ordering systems.  This means that espa-web knows how to capture user orders, validate parameters, determine order + product disposition (including placing & monitoring orders for level 1 data), notifying users of completed orders and providing access to download completed products.  It also provides services for espa-production to retrieve production requests and to capture production status updates.

espa-web currently captures user orders from two sources: The espa.cr.usgs.gov website itself and also USGS Earth Explorer.  Orders are obtained from USGS EE via web services hosted by the LTA project.

#### espa-production
espa-production is responsible for receiving production requests, validating the requests, locating and using any necessary auxillary data, transferring level 1 data to a working directory, executing the necessary science algorithms to produce the product, placing the finished product in a distribution location and finally notifying espa-web that the production request is complete.  espa-production is a stateless system, with each production run remaining isolated from any other.

## General Capabilities That May or May Not Be Properly Advertised
Later in this document, there are a series of requirements and capabilities that do not seem to belong together in the same system.  For instance, there are a variety of datasets that ESPA cannot do anything with science-wise.  MODIS data itself is never enhanced by ESPA in any way.  So why include it then if we can't create derivative products?  The short answer is, 'we can'.  Here's how:

* Dynamic Tile Genertion 
  * We can give you stacks of images lined up properly with one another.
  * Specify projection with proper parameters
  * Specify output extents in meters
  * Specify pixel size
  * Specify resampling method.
  * The resulting output is proven to always align.

* Sensor Intercomparison Via Statistics And Plotting
  * By choosing coincident observations from different sensors (MODIS 09 + Landsat SR over the same place on the Earth and acquired close to the same time), users are able to plot and compare the performance of each sensor/algorithm in relation to one another.  This is particularly useful when users would like to establish levels of confidence in a particular sensor, compare new sensors with old, or otherwise normalize reading they are seeing from a variety of sources.
   
* Simple format conversion
  * Perhaps users need to acquire large quantities of imagery but they would like in binary (envi), hdf-eos2 or geotiff.  ESPA format converters are pluggable so if other formats are desired they can easily be developed and hosted.
   
* Metadata
  * Landsat product level metadata (which differs from the bulk metadata that is accessible) is not available to end users without downloading the images as well.  ESPA can do this by only requesting Original Input Metadata
  * ESPA output product metadata (for anything other than Original Input Products/Original Input Metadata) is in a schema constrained XML format.  This means ESPA metadata files can be transformed with standardized tooling like XSLT stylesheets.  If end-users are validating the imagery they receive from ESPA with the publicly accessible XML schema, they can be 100% assured that their software is still compatible with ESPA output products.  In fact, ESPA itself uses schema validation internally before distributing products to ensure the integrity of our production pipeline.

## Why create an API?
As previously discussed above, the original system was built solely as a temporary incubation platform for science products.  The only original requirement was to produce 450 SR corrections to level 1 data per day and make the outputs available to end users, and to (obviously) accomplish this work as quickly and cheaply as possible.  For context, ESPA now is capable of performing over 23,000 SR corrections per day (as of October 2015).  The capacity increases have been driven purely by demand.

New requirements have emerged from the science community that detail the need to perform deep time series analysis against atmospherically corrected observations.  This body of work is being accompished as part of the LCMAP project.  LCMAP requires (or will in the near future) the full Landsat archive corrected to surface reflectance, first for the continental United States & Alaska, and later globally.  It also requires any new observations to be corrected so they can be incorporated into it's output products.

ESPA currently provides access to order data via web interfaces only. (espa.cr.usgs.gov and earthexplorer.usgs.gov).  This is clearly inadequate to establish an automated pipeline for ongoing analysis: No human wants to manually order, track and transfer millions of scenes. The ESPA system must be modified to provide an application programming interface for downstream systems to gain access to its capabilities.

## Domain Entities, Constraints, Rules, Requirements
1. **The system captures a user supplied list of input observations, desired output products and customizations and groups this as an order.**  
  1. The user supplied list of input observations is a newline `\n` separated file with each line containing a Landsat scene id or MODIS tile id.  
  2. TM, ETM+, OLI, OLI/TIRS, MODIS 09A1, MODIS 09GA, MODIS 09GQ, MODIS 09Q1, MODIS 13A1, MODIS 13A2, MODIS 13A3 and MODIS 13Q1 products may be supplied as inputs.  
  3. Input products must be available from an automated source such as LTA DDS or the LPDAAC Data Pool.
  
2. **The available output product list varies with each input type.**  
  1. Example: OLI & MODIS products cannot be corrected to surface reflectance.  OLI cannot due to not having thermal data available for cloud detection.  MODIS 09 products are *already* at surface reflectance and MODIS 13 products are merely a vegetation index.  
  
3. **The available output products list varies *within* each input type.**  
  1. Example: Not all Landsat TM/ETM+/OLITIRS scenes can be corrected to surface reflectance, particularly nighttime observations.  
  
4. **The available output product list varies based on the spatial and temporal characterics of the input observations.**  
  1. Example: Land Surface Temperature cannot currently be produced outside of certain geographic extents due to insufficient auxillary data.  
  
5. **Requests for output customization are captured at the order (not the input observation) level.  These customizations are applied against every ESPA output product in the order.**  
  1. Users may request that their order is reprojected to sinusoidal, albers, UTM, geographic or polar stereographic.  Each projection requires its own set of parameters which must be validated.  
  2. Users may request their order is output in binary (envi), HDF EOS2, or GeoTiFF format.  
  3. Users may request modification of the spatial output extents (spatial subsetting) of all output products in either projection coordinates or decimal degrees.  If geographic projection is requested, coordinates may only be provided in decimal degrees.
  4. Users may request pixel resizing of the output products in either meters or decimal degrees, depending on the requested projection.  Geographic will accept only decimal degrees for the pixel size whereas all true projections (all others available) require meters.
  5. Where necessary, users may choose their desired resampling method.  
  6. Users may not perform spatial subsetting without first requested reprojection.  This is due to input observations arriving in varying projections, making projection coordinates meaningless.  
  
6. **The system approaches processing in an all or nothing fashion:  If a user requests SR and TOA and SR fails, the entire scene is marked as unavailable (even though TOA may have actually been available and must be produced prior to performing SR)**

7. **Users may request statistics and plotting of statistics on any order** 


## Assumptions
1. The proposed API will be logically divided into a user API, system API and admin API.  
    * The user api will accept orders and provide end user access to order/product status and links to download completed products.
    * The system API serves functionality to espa-production, mainly for obtaining production requests and capturing production status.  
    * The admin API will allow operations & maintenance staff to monitor and manipulate the system as needed.

2. All calls will be made over HTTPS only and will require HTTP Basic Authentication.
    * Users will be authenticated against the ERS.  Credentials used for EarthExplorer are used here.
    * The exception to this is the call to authenticate.  This call is needed so clients are able to determine if a user should even be allowed to perform operations.  This can later be modified to return roles.

3. Each operation will be stateless.  Sessions, cookies, etc will not be used.

4. Any payloads for POST or PUT operations will be valid JSON.  GET responses will also be JSON.

5. Traffic control (rates, locations, blacklists, etc) will be handled by an HTTP(S) proxy layer.

6. Users are not currently limited in the amounts of imagery they may request.  Backend queuing ensures fair access.


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
* To be defined

## Proposed Admin API Operations
* To be defined

###### Version 0 Demo (October 2015)
* Created to display url design for comment and review
* 

## Output Product Availability By Input Type
### Level 1 Data
|  | Original Level 1 Data | Original Level 1 Metadata | Customized Level 1 Data |
|:------------- |:------------- |:------------- |:------------- |
| Landsat 4 TM | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| Landsat 5 TM | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| Landsat 7 ETM+ | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| Landsat 8 OLI | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| Landsat 8 TIRS | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| Landsat 8 OLITIRS | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| MODIS 09A1  | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| MODIS 09GA  | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| MODIS 09GQ  | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| MODIS 09Q1  | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| MODIS 13A1  | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| MODIS 13A2  | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| MODIS 13A3  | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|
| MODIS 13Q1  | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:|

### ESPA CDR/ECV Outputs
|  | TOA | SR | BT | LST | DSWE |
|:------------- |:------------- |:------------- |:------------- |:------------- |:------------- |
| Landsat 4 TM | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Landsat 5 TM | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Landsat 7 ETM+ | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Landsat 8 OLI | :heavy_check_mark: | :x: | :x: | :heavy_check_mark: | :heavy_check_mark: |
| Landsat 8 TIRS | :x: | :x: |:heavy_check_mark:| :x: | :x: |
| Landsat 8 OLITIRS | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| MODIS 09A1  | :x: | :x: | :x: | :x: | :x: |
| MODIS 09GA  | :x: | :x: | :x: | :x: | :x: |
| MODIS 09GQ  | :x: | :x: | :x: | :x: | :x: |
| MODIS 09Q1  | :x: | :x: | :x: | :x: | :x: |
| MODIS 13A1  | :x: | :x: | :x: | :x: | :x: |
| MODIS 13A2  | :x: | :x: | :x: | :x: | :x: |
| MODIS 13A3  | :x: | :x: | :x: | :x: | :x: |
| MODIS 13Q1  | :x: | :x: | :x: | :x: | :x: |

### ESPA Spectral Indices
|  | NDVI | EVI | SAVI | MSAVI | NDMI | NBR | NBR2 |
|:------------- |:------------- |:------------- |:------------- |:------------- |:------------- |:------------- | :------------- |
| Landsat 4 TM | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Landsat 5 TM | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Landsat 7 ETM+ | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark:| :heavy_check_mark:| :heavy_check_mark: |
| Landsat 8 OLI | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Landsat 8 TIRS | :x: | :x: | :x: | :x: | :x: | :x:| :x: |
| Landsat 8 OLITIRS | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| MODIS 09A1 | :x: | :x: | :x: | :x: | :x: | :x: | :x: |
| MODIS 09GA | :x: | :x: | :x: | :x: | :x: | :x: | :x: |
| MODIS 09GQ | :x: | :x: | :x: | :x: | :x: | :x: | :x: |
| MODIS 09Q1  | :x: | :x: | :x: | :x: | :x: | :x: | :x: |
| MODIS 13A1  | :x: | :x: | :x: | :x: | :x: | :x: | :x: |
| MODIS 13A2  | :x: | :x: | :x: | :x: | :x: | :x: | :x: |
| MODIS 13A3  | :x: | :x: | :x: | :x: | :x: | :x: | :x: |
| MODIS 13Q1  | :x: | :x: | :x: | :x: | :x: | :x: | :x: |

### Notes
Statistics and plotting are available for all ESPA output products.

MODIS products are not generally available for additional processing levels as they have already been processed to a level beyond level 1 by the datasource: MODIS 09 series is at surface reflectance and the 13 series is NDVI.

## Projections and Parameters
#### Albers Equal Area `(aea)`
| Parameter  | Units | Minimum Value | Maximum Value |
|:------------- |:------------- |:------------- |:------------- |
| Latitude Of Origin  | decimal degrees | -90.0 | 90.0 |
| Central Meridian | decimal degrees | -180.0 |180.0|
| 1st Standard Parallel | decimal degrees | -90.0 | 90.0 |
| 2nd Standard Parallel | decimal degrees | -90.0 | 90.0 |
| False Easting | floating point | any  | any |
| False Northing | floating point | any | any |

Datum is selectable from `WGS84` (default), `NAD27`, and `NAD83`

#### Universal Transverse Mercator `(utm)`
| Parameter  | Units | Minimum Value | Maximum Value |
|:------------- |:------------- |:------------- |:------------- |
| UTM Zone  | Integer | 1 | 60 |
| UTM Zone North South| North or South |  |  |

#### Sinusoidal `(sinu)`
| Parameter  | Units | Minimum Value | Maximum Value |
|:------------- |:------------- |:------------- |:------------- |
| Central Meridian | decimal degrees | -180.0 |180.0|
| False Easting | floating point | any | any |
| False Northing | floating point | any | any |

#### Polar Sterographic `(ps)`
| Parameter  | Units | Minimum Value | Maximum Value |
|:------------- |:------------- |:------------- |:------------- |
| Longitudinal Pole | decimal degrees | -180.0 |180.0|
| Latitude True Scale | decimal degrees | -90.0 or 60.0 | -60.0 or 90.0|
| False Easting | floating point | any | any |
| False Northing | floating point | any | any |

Latitude True Scale must fall within the range of -90.0 to -60.0 OR 60.0 to 90.0

#### Geographic `(lonlat)`
No parameters are required for Geographic.

## Spatial Subsetting
Spatial subsetting may be accomplished once a user has selected a target projection.  There are several reasons for this.

1. **The primary purpose of spatial subsetting is to establish a common frame for the resulting images.**  
  Each image that is subset should be framed exactly the same as all others that have also been subset with the same parameters.  This goes without saying.  

2. **ESPA input data is in multiple projections.**  
  MODIS data is sinusoidal, some Landsat is in UTM, other Landsat is in polar stereographic.  If a user specified meter based spatial extents without forcing all rasters into a common projection then each different type would be subset differently, or not at all (fail to warp.)  Moreover, it is impossible to know (given the limited user interface) which projection the user was thinking in when specifying the coordinates without forcing a common geometry.  

3. **Simply allowing geographic subset coordinates without specifying a target projection seems like it *should* work, but does not.**  
Decimal degrees represent points on a sphere whereas projection coordinates are just x,y on a flat 2d grid.  When users are specifying decimal degrees, they are really asking for all data inclusively within the geographic region.  In order to provide this a minbox operation must be performed to determine the real maximum extent the image must be cropped to.  
  2. The above operation *could* be performed without reprojection, but the image would have to be projected (deprojected) to geographic, the minbox operation performed, then reprojected back into the original projection.  ESPA cannot always determine what parameters were used in the original projection, plus the forced resampling is irreversibly altering the image data.  
  3. The only way to reliably produce images in a common frame (and ensure all the pertinent data is included) is to deal with the images in 2D projection space.  The geographic minbox operation will always result in an indeterminate (at warp time) output frame, thus the pixel at the upper left of the image will rarely be the same geographic location on the Earth.

## Pixel Resizing
ESPA can alter the pixel size (thus increasing or decreasing the overall resolution) of it's output products.  Values are supplied in meters unless the images are being deprojected into geographic, at which point they are then specified in decimal degrees.

Meter based pixel sizes can be specified from `30.0` to `1000.0` meters inclusively.
Decimal degree pixels may be set from `0.0002695` to `0.0089831`, which coorelate roughly to the meters based range (depending on the geographic location on the Earth).

During any operation that requires resampling, the user may select from `Nearest Neighbor` (default), `Bilinear Interpolation`, and `Cubic Convolution`.

## Acronyms 
| Term | Definition |
|:------------- |:------------- |
| API           | Application Programming Interface |
| BT            | Brightness Temperature |
| DDS           | Data Distribution Service |
| DSWE          | Dynamic Surface Water Extent |
| EROS          | Earth Resources Observations and Science Center|
| ERS           | EROS Registration System |
| ESPA          | EROS Science Processing Architecture |
| ETM+          | Enhanced Thematic Mapper +|
| EVI           | Enhanced Vegetation Index |
| HDF EOS2      | Hierarchical Data Format Earth Observation Systems 2|
| HTTP          | Hyper Text Transfer Protocol |
| HTTPS         | Hyper Text Transfer Protocol Secure|
| JSON          | Javascript Object Notation |
| LCMAP         | Land Change Monitoring Assessment and Prediction|
| LST           | Land Surface Temperature |
| LTA           | Long Term Archive      |
| LPDAAC        | Land Process Distributed Active Archive |
| MODIS         | Moderate Resolution Imaging Spectroradiometer |
| MSAVI         | Modified Soil Adjusted Vegetation Index |
| NBR           | Normalized Burn Ratio |
| NBR2          | Normalized Burn Ratio 2 |
| NDMI          | Normalized Difference Moisture Index |
| NDVI          | Normalized Difference Vegetation Index |
| OLI           | Operational Land Imager |
| OLI/TIRS      | Operational Land Imager/Thermal Infrared Sensor |
| SAVI          | Soil Adjusted Vegetation Index |
| SR            | Surface Reflectance |
| TOA           | Top Of Atmosphere |
| TIRS          | Thermal Infrared Sensor |
| TM            | Thematic Mapper |
| USGS          | United States Geological Survey |
| UTM           | Universal Transverse Mercator |
