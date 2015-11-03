## Comments from Chris May, 11/3/15
1. Any external service calls ESPA makes needs to employ caching
2. Provide an 'expires' field on orders for when they will be removed from cache
3. Distribution of orders fulfilled by ESPA need to remain with ESPA.  That is, if users place orders through an
client that uses ESPA for fulfillment, then the users should ultimately wind up obtaining their completed orders from
the ESPA website itself.
4. Service operation mod for determining ESPA production capabilities.
  API users need to be able to call a service operation to determine what output products ESPA can make for a given input product.

  The caller supplies a list of inputs and ESPA returns a dictionary of inputs to valid output product types.  The output should be able to be organized either by (a) input product (b) output product (c) ESPA dataset (d) LTA dataset.
  
  The caller should also be able to supply a query parameter that specifies the output product of interest.  e.g., supply a list of inputs and a target output product 'sr' or 'sr_ndvi'.  This would trim down on a lot of network traffic in cases where this is all that's needed.
  
  The LTA name should be provided in the returned calls.
  
  The LTA name should also be provided for MODIS products (current system does not have this information.)
    The LTA name for MODIS is MODIS_<shortname>
