# espa-api
Demo API for the ESPA ordering & scheduling system.  

## Related Pages
* [API Interface](docs/API-INTERFACE.md)
* [Available Products](docs/AVAILABLE-PRODUCTS.md)
* [Abbreviations & Definitions](docs/TERMS.md)
* [ESPA Customizations](docs/CUSTOMIZATION.md)
* [Requirements & Assumptions](docs/API-REQUIREMENTS.md)
* [Review Comments](docs/REVIEW-COMMENTS.md)


## ESPA System Overview
ESPA is a system for producing advanced science products from existing products. It was originally constructed to serve as a temporary production platform for science algorithms under incubation but has since transitioned into a quasi-operational state within USGS EROS, due primarily to the popularity of its products.

ESPA operates on a scene by scene basis and was built to produce many products at once rather than a single product as quickly as possible (multiprocess vs multithreading).  When a product algorithm executes, it only has access to the spatial and temporal context of the observation in question, save any auxiliary data needed such as ozone or water pressure measurements.  The system is therefore highly optimized for single-scene processing but is wholly unsuited for compositing, mosaicing, time-series analysis or any other operation that requires information from a separate observation.

The system is composed of two major subsystems, espa-web and espa-production.

#### espa-web
espa-web provides all the ordering & scheduling operations for the system, as well as the majority of the integration with the rest of USGS EROS ordering systems.  This means that espa-web knows how to capture user orders, validate parameters, determine order + product disposition (including placing & monitoring orders for level 1 data), notifying users of completed orders and providing access to download completed products.  It also provides services for espa-production to retrieve production requests and to capture production status updates.

espa-web currently captures user orders from two sources: The http://espa.cr.usgs.gov website and also USGS Earth Explorer.  Orders are obtained from USGS EE via web services hosted by the LTA project.

#### espa-production
espa-production is responsible for receiving production requests, validating the requests, locating and using any necessary auxiliary data, transferring level 1 data to a working directory, executing the necessary science algorithms to produce the product, placing the finished product in a distribution location and finally notifying espa-web that the production request is complete.  espa-production is a stateless system, with each production run remaining isolated from any other.

---

## General Capabilities (Which May or May Not Be Properly Advertised)
The ESPA system covers a series of requirements and capabilities that do not seem to belong together at first glance.  For instance, there are a variety of datasets that ESPA cannot perform any additional science against:  MODIS data itself is never enhanced by ESPA in any way.  So why include it then if we can't create derivative products?  The short answer is it can.  Here are the system's overall capabilities.

* **Climate Data Record & Essential Climate Variable Production**
  * Landsat inputs only See [available products](docs/AVAILABLE_PRODUCTS.md)
  * Scenes are input
  * Additional science algorithms are applied
  * Derivative products are output
  
* **Non-composited Tile Generation**  
  ESPA can produce stacks of images lined up properly with one another in line/sample space.  When customization is requested for an order, it is applied to every output product whether that be customized input products (level 1), toa, sr or indices.  The only thing that will bypass customization are Original Input Products, which are delivered untouched exactly as they were received from the upstream system(s).

  No compositing or mosaicing is applied during these operations, thus the outputs from ESPA will be images that are projected and framed as specified but may be sparsely populated, depending on the spatial extent of the input and the requested output extent.

  Users can create non-composited tiles by following these steps:
  * Request scenes/tiles that contain data within the geographic region of interest (required)
  * Select Customized Input Products (if MODIS or Landsat Level 1 products should be tiled) and/or CDR/ECV/SI products (required)
  * Specify output projection with proper parameters (required) [See projections](docs/CUSTOMIZATION.md)  
  * Specify output extents in meters (required) [See output extents](docs/CUSTOMIZATION.md)  
  * Specify pixel size (optional) [See pixel resizing](docs/CUSTOMIZATION.md)  
  * Specify resampling method. (required) [See resampling](docs/CUSTOMIZATION.md)  
   
  Output images from an order that has satisfied these conditions will be properly aligned & framed to one another. 
  The onus is on the user to maintain and track their grid and tile definitions (projections with parameters & output extents).  **_Simply requesting scenes to be reprojected is not enough to line up the outputs_**.  A fixed set of output spatial extents must be provided to create a consistent output image frame.

  It is also worth noting that ESPA will deliver exactly what the request specified insofar as spatial extents are concerned.  It does not 'snap' to the nearest 30 meter pixel for example.

* **Sensor Intercomparison Via Statistics And Plotting**  
  By choosing coincident observations from different sensors (MODIS 09 + Landsat SR over the same place on the Earth and acquired close to the same time), users are able to plot and compare the performance of each sensor/algorithm in relation to one another.  

  This is particularly useful when users would like to establish levels of confidence in a particular sensor, compare new sensors with old, or normalize measurements obtained from a variety of sources.
   
* **Simple format conversion**  
  Users may alter the file format for output images. Current available formats are binary (envi), hdf-eos2 or geotiff.  Binary BIP (band interleaved by pixel) is in work.  ESPA format converters are pluggable modules so if other formats are desired they can easily be developed and hosted.
   
* **Metadata**  
  Landsat product metadata (which differs from what's available via the Landsat Bulk Metadata Service) is not available to end users without downloading the images as well.  ESPA can deliver the level 1 product metadata without the accompanying rasters by requesting Original Input Metadata.  This was never a driving requirement but more of a no-cost capability made possible by using level 1 data as an input to CDRs and ECVs.

  ESPA output product metadata (for anything other than Original Input Products/Original Input Metadata) is in a schema constrained XML format.  This means ESPA metadata files can be transformed with standardized tooling like XSLT stylesheets.
  
  If end-users are validating the imagery they receive from ESPA with the publicly accessible XML schema, they can be 100% assured that their software is still compatible with ESPA output products.  In fact, ESPA itself uses schema validation internally before distributing products to ensure the integrity of its production pipeline.

## Why create an API?
The original system was built as a temporary incubation platform for science products.  The only real requirement was to produce 450 SR corrections per day, make the outputs available to end users, and to (obviously) accomplish this work as quickly and cheaply as possible.  The system has grown to handle 23,000 SR corrections per day (as of October 2015) and is relied upon as the definitive source for these products.  This situation has been driven purely by demand.

New requirements have emerged from the science community that detail the need to perform deep time series analysis against atmospherically corrected observations.  This body of work is being accomplished by the LCMAP project.  LCMAP requires (or will in the near future) the full Landsat archive corrected to surface reflectance, first for the continental United States & Alaska, and later globally.  It will also require any new observations to be corrected so they can be incorporated into its output products.

Currently, ESPA orders may only be placed via web interface: http://espa.cr.usgs.gov and http://earthexplorer.usgs.gov.  This is clearly inadequate to establish an automated pipeline for ongoing analysis as no human wants to manually order, track and transfer millions of scenes. The ESPA system must be modified to provide an application programming interface for downstream systems to gain access to its capabilities.
