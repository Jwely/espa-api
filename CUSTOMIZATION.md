## Projections and Parameters
ESPA supported projections and the parameters necessary for each are captured below.

| Projection | Parameter  | Units | Values |
|:------------- |:------------- |:------------- |:------------- |
| **Albers Equal Area** `(aea)` |  | | |
| | Latitude Of Origin  | decimal degrees | -90.0 to 90.0 |
| | Central Meridian | decimal degrees | -180.0 to 180.0 |
| | 1st Standard Parallel | decimal degrees | -90.0 to 90.0 |
| | 2nd Standard Parallel | decimal degrees | -90.0 to 90.0 |
| | False Easting | floating point | any float |
| | False Northing | floating point | any float |
| | Datum | string | WGS84 (default), NAD27, or NAD83 |
| **UTM** `(utm)` | | | |
| | UTM Zone  | integer | 1 to 60 |
| | UTM Zone North South | string | North or South |
| **Sinusoidal** `(sinu)` | | | |
| | Central Meridian | decimal degrees | -180.0 to 180.0|
| | False Easting | floating point | any float |
| | False Northing | floating point | any float |
| **Polar Sterographic** `(ps)` | | | |
| | Longitudinal Pole | decimal degrees | -180.0 to 180.0|
| | Latitude True Scale | decimal degrees | -90.0 to -60.0 or 60.0 to 90.0 |
| | False Easting | floating point | any float |
| | False Northing | floating point | any float |
| **Geographic** `(lonlat)` | | | |
| | None | None  | None  |

---

## Spatial Subsetting (Output Extents)
Establishing fixed output extents for images may be accomplished by first selecting a target projection and then supplying the upper left x, upper left y, lower right x and lower right y values for the desired output frame.

If the target projection is Geographic (lonlat), the supplied values must be in decimal degrees.  If any other projection is chosen, the coordinates are in meters (in projection space).

Inquiries have been made as to why ESPA forces the user to reproject before allowing spatial subsetting.  There are several reasons for this.  

1. **The primary purpose of spatial subsetting is to establish a common frame for the resulting images.**  
  Each image that is subset should be framed exactly the same as all others that have also been subset with the same parameters.  This goes without saying.  

2. **ESPA input data is in multiple projections.**  
  MODIS data is sinusoidal, some Landsat is in UTM, other Landsat is in polar stereographic.  If a user specified meter based spatial extents without forcing all rasters into a common projection then each type would be subset differently, or not at all (fail to warp.)  It is not possible to determine which projection the user was thinking in when specifying coordinates without forcing a common geometry.  

3. **Simply using geographic subset coordinates without specifying a target projection seems like it *should* work, but does not.**  
  Decimal degrees represent points on a sphere whereas projection coordinates represent x & y on a flat 2 dimensional grid.  Performing a direct subset of the imagery using coordinates such as this results in data loss, as the delivered imagery is always a two dimensional representation of a spheroid.

  Users specifying a subset box in decimal degrees are really asking for all data inclusively within the geographic region.  In order to provide this a minbox operation must be performed to determine the real extents an image must be cropped to.  This is done by walking the edges of the image to find the maximum data extents and then adjusting the requested decimal degree coordinates accordingly.

  The above operation *could* be performed without a user specified target projection, but the image would have to be deprojected to geographic, the minbox operation performed, the subset performed, then an image warp back into the original projection.  ESPA cannot always determine what parameters were used in the original projection, plus the forced resampling is irreversibly altering the image data.
  
  The only way to reliably produce images in a common frame (and ensure all the pertinent measurements are included) is to deal with the images in a known 2D projection space.  The geographic minbox operation will always result in an indeterminate (at warp time) output frame, thus the pixel at the upper left of the image will rarely be the same geographic location on the Earth, resulting in pixel misalignment.

## Pixel Resizing
ESPA can alter the pixel size (thus increasing or decreasing the overall resolution) of it's output products.  Values are supplied in meters unless the images are being deprojected into geographic, at which point they are then specified in decimal degrees.

Meter based pixel sizes can be specified from `30.0` to `1000.0` meters inclusively.
Decimal degree pixels may be set from `0.0002695` to `0.0089831`, which coorelate roughly to the meters based range (depending on the geographic location on the Earth).

During any operation that requires resampling, the user may select from `Nearest Neighbor` (default), `Bilinear Interpolation`, and `Cubic Convolution`.
