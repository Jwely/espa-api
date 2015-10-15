from cerberus import Validator
import yaml

albers = '''
standard_parallel_1:
  type: float
  min:-90.0
  max:90.0
standard_parallel_2:
  type: float
  min:-90.0
  max:90.0
central_meridian:
  type: float
  min:-180.0
  max:180.0
latitude_of_origin:
  type: float
  min: -90.0
  max: 90.0
false_easting:
  type: float
false_northing:
  type: float
datum:
  type: string
  allowed: wgs84, nad27, nad83
'''

utm = '''
zone:
  type: integer
  min: 1
  max: 60
zone_ns:
  type: string
  allowed: north, south
'''

geographic = '''
'''

sinusoidal = '''
central_meridian:
  type: float
  min: -180.0
  max: 180.0
false_easting:
  type: float
false_northing:
  type: float   
'''

polar_stereographic = '''
longitudinal_pole:
  type: float
  min: -180.0
  max: 180.0
latitude_true_scale:
  type: latitude_true_scale
'''

schema_text = '''
name: 
  type: string
age:
  type: integer
  min: 10
projection:
  type: string
  allowed: aea, sinu, ps, utm
image_extents:
  north:
  south:
  east:
  west:
'''

class ESPAValidator(Validator):

    def _validate_type_latitude_true_scale(self, field, value):
        ''' Custom type to support the float range for latitude_true_scale values '''
        try:
            _value = float(value)
            if not ((_value >= -90.0 and _value <= -60.0) or 
                   (_value >= 60.0 and _value <= 90.0)):
                raise ValueError()
        except ValueError:
            self._error(field, 'valid range is -90.0 to -60.0 or 60.0 to 90.0')


