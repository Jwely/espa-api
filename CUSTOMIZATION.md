## Projections and Parameters
ESPA supported projections and the parameters necessary for each are captured below.

---

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

---

#### Universal Transverse Mercator `(utm)`
| Parameter  | Units | Minimum Value | Maximum Value |
|:------------- |:------------- |:------------- |:------------- |
| UTM Zone  | Integer | 1 | 60 |
| UTM Zone North South| North or South |  |  |

---

#### Sinusoidal `(sinu)`
| Parameter  | Units | Minimum Value | Maximum Value |
|:------------- |:------------- |:------------- |:------------- |
| Central Meridian | decimal degrees | -180.0 |180.0|
| False Easting | floating point | any | any |
| False Northing | floating point | any | any |

---

#### Polar Sterographic `(ps)`
| Parameter  | Units | Minimum Value | Maximum Value |
|:------------- |:------------- |:------------- |:------------- |
| Longitudinal Pole | decimal degrees | -180.0 |180.0|
| Latitude True Scale | decimal degrees | -90.0 or 60.0 | -60.0 or 90.0|
| False Easting | floating point | any | any |
| False Northing | floating point | any | any |

Latitude True Scale must fall within the range of -90.0 to -60.0 OR 60.0 to 90.0

---

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
