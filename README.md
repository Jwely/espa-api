# espa-api
Demo API for the ESPA ordering & scheduling system.  

## Related Pages
* [API Interface](API-INTERFACE.md)
* [Available Products](AVAILABLE_PRODUCTS.md)
* [Abbreviations & Definitions](TERMS.md)
* [ESPA Customizations](CUSTOMIZATION.md)
* [Requirements & Assumptions](API-REQUIREMENTS.md)


## Overview
The ESPA project is a system for producing advanced science products from existing products. It was originally constructed to serve as a production platform for science algorithms under incubation but has since transitioned into a quasi-operational state within USGS EROS, due primarily to the popularity of it's products.

ESPA operates on a scene by scene basis and was built to produce many products at once rather than a single product as quickly as possible (multiprocess vs multithreading).  Each product algorithm execution only has access to the spatial and temporal context of the observation in question, save any auxillary data needed such as ozone or water pressure measurements.  ESPA is therefore highly optimized for single-scene (observation) but is wholly unsuited for compositing, mosaicing, or time-series analysis, or any other operation that requires information from a separate observation.

The system is composed of two major subsystems, espa-web and espa-production.

#### espa-web
espa-web provides all the ordering & scheduling operations for the system, as well as the majority of the integration with the rest of USGS EROS ordering systems.  This means that espa-web knows how to capture user orders, validate parameters, determine order + product disposition (including placing & monitoring orders for level 1 data), notifying users of completed orders and providing access to download completed products.  It also provides services for espa-production to retrieve production requests and to capture production status updates.

espa-web currently captures user orders from two sources: The espa.cr.usgs.gov website itself and also USGS Earth Explorer.  Orders are obtained from USGS EE via web services hosted by the LTA project.

#### espa-production
espa-production is responsible for receiving production requests, validating the requests, locating and using any necessary auxillary data, transferring level 1 data to a working directory, executing the necessary science algorithms to produce the product, placing the finished product in a distribution location and finally notifying espa-web that the production request is complete.  espa-production is a stateless system, with each production run remaining isolated from any other.

---

## General Capabilities (Which May or May Not Be Properly Advertised)
Later in this document, there are a series of requirements and capabilities that do not seem to belong together in the same system.  For instance, there are a variety of datasets that ESPA cannot do anything with science-wise:  MODIS data itself is never enhanced by ESPA in any way.  So why include it then if we can't create derivative products?  The short answer is we can.  Here are the system's overall capabilities.

* Climate Data Record & Essential Climate Variable Production
  * A Landsat scene is input
  * Additional science algorithms are applied
  * A new science product is output

* Dynamic Tile Generation 
  * ESPA can produce stacks of images lined up properly with one another.
  1. Request scenes/tiles that contain data within the geographic region of interest (required)
  2. Select Customized Input Products (if MODIS or Landsat Level 1 products should be tiled) and/or CDR/ECV/SI products (required)
  3. Specify output projection with proper parameters (required)
  4. Specify output extents in meters (required)
  5. Specify pixel size (optional)
  6. Specify resampling method. (required)
  7. The resulting output images are proven to align.
  * The onus is on the user to maintain and track their grid and tile definitions.
    * Projection with parameters, output extents, output pixel sizes
  * Simply requesting scenes to be reprojected is not enough to line up the outputs.  A fixed set of output spatial extents must be provided to create a consistent output image frame.

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

###### Version 0 Demo (October 2015)
* Created to display url design for comment and review
* 
