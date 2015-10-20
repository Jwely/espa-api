## Domain Entities, Constraints, Rules, Requirements
1. **The system captures a user supplied list of input observations, desired output products and customizations and groups this as an order.**  
  1. The user supplied list of input observations is a newline `\n` separated file with each line containing a Landsat scene id or MODIS tile id.  
  2. TM, ETM+, OLI, OLI/TIRS, MODIS 09A1, MODIS 09GA, MODIS 09GQ, MODIS 09Q1, MODIS 13A1, MODIS 13A2, MODIS 13A3 and MODIS 13Q1 products may be supplied as inputs.  
  3. Input products must be available from an automated source such as LTA DDS or the LPDAAC Data Pool.
  
2. **The available output product list varies with each input type.**  
  1. Example: OLI & MODIS products cannot be corrected to surface reflectance.  OLI cannot due to not having thermal data available for cloud detection.  MODIS 09 products are *already* at surface reflectance and MODIS 13 products are merely a vegetation index.  
  
3. **The available output products list varies *within* each input type.**  
  1. Example: Not all Landsat TM/ETM+/OLITIRS scenes can be corrected to surface reflectance, particularly nighttime observations.  
  
4. **The available output product list varies based on the spatial and temporal characteristics of the input observations.**  
  1. Example: Land Surface Temperature cannot currently be produced outside of certain geographic extents due to insufficient auxiliary data.  
  
5. **Requests for output customization are captured at the order (not the input observation) level.  These customizations are applied against every ESPA output product in the order.**  
  1. Users may request that their order is reprojected to sinusoidal, albers, UTM, geographic or polar stereographic.  Each projection requires its own set of parameters which must be validated.  
  2. Users may request their order is output in binary (envi), HDF EOS2, or GeoTiFF format.  
  3. Users may request modification of the spatial output extents (spatial subsetting) of all output products in either projection coordinates or decimal degrees.  If geographic projection is requested, coordinates may only be provided in decimal degrees.
  4. Users may request pixel resizing of the output products in either meters or decimal degrees, depending on the requested projection.  Geographic will accept only decimal degrees for the pixel size whereas all true projections (all others available) require meters.
  5. Where necessary, users may choose their desired resampling method.  
  6. Users may not perform spatial subsetting without first requesting reprojection.  This is due to input observations arriving in varying projections, making projection coordinates meaningless.  
  
6. **The system approaches processing in an all or nothing fashion:  If a user requests SR and TOA and SR fails, the entire scene is marked as unavailable (even though TOA may have actually been available and must be produced prior to performing SR)**

7. **Users may request statistics and plotting of statistics on any order** 


## Assumptions
1. The proposed API will be logically divided into a user API, production API and admin API.  
    * The user api will accept orders and provide end user access to order/product status and links to download completed products.
    * The production API serves functionality to espa-production, mainly for obtaining production requests and capturing production status.  
    * The admin API will allow operations & maintenance staff to monitor and manipulate the system as needed.

2. All calls will be made over HTTPS only and will require HTTP Basic Authentication.
    * Users will be authenticated against the ERS.  Credentials used for EarthExplorer are used here.
    * The exception to this is the call to authenticate.  This call is needed so clients are able to determine if a user should even be allowed to perform operations.  This can later be modified to return roles.
    * espa-production will rely on a system level account not housed in ERS.
    * Roles restricting access to the production and admin api will be kept within the ESPA system.

3. Each operation will be stateless.  Sessions, cookies, etc will not be used.

4. Any payloads for POST or PUT operations will be valid JSON.  GET responses will also be JSON.

5. Traffic control (rates, locations, blacklists, etc) will be handled by an HTTP(S) proxy layer.

6. Users are not limited in the quantity of imagery they request.  Backend queuing ensures fair access.
