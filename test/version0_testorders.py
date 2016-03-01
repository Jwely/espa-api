import copy
import collections

import api.domain.sensor as sn
import validictory
from validictory import validator

good_test_projections = {'aea': {'standard_parallel_1': 29.5,
                                 'standard_parallel_2': 45.5,
                                 'central_meridian': -96,
                                 'latitude_of_origin': 23,
                                 'false_easting': 0,
                                 'false_northing': 0,
                                 'datum': 'nad83'},
                         'utm': {'zone': 33,
                                 'zone_ns': 'south'},
                         'lonlat': None,
                         'sinu': {'central_meridian': 0,
                                  'false_easting': 0,
                                  'false_northing': 0},
                         'ps': {'longitudinal_pole': 0,
                                'latitude_true_scale': 75}}


def build_base_order():
    """
    Builds the following dictionary (with the products filled out from sensor.py):

    base = {'MOD09A1': {'inputs': 'MOD09A1.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MOD09GA': {'inputs': 'MOD09GA.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MOD09GQ': {'inputs': 'MOD09GQ.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MOD09Q1': {'inputs': 'MOD09Q1.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MYD09A1': {'inputs': 'MYD09A1.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MYD09GA': {'inputs': 'MYD09GA.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MYD09GQ': {'inputs': 'MYD09GQ.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MYD09Q1': {'inputs': 'MYD09Q1.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MOD13A1': {'inputs': 'MOD13A1.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MOD13A2': {'inputs': 'MOD13A2.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MOD13A3': {'inputs': 'MOD13A3.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MOD13Q1': {'inputs': 'MOD13Q1.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MYD13A1': {'inputs': 'MYD13A1.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MYD13A2': {'inputs': 'MYD13A2.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MYD13A3': {'inputs': 'MYD13A3.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'MYD13Q1': {'inputs': 'MYD13Q1.A2000072.h02v09.005.2008237032813',
                        'products': ['l1']},
            'tm4': {'inputs': 'LT42181092013069PFS00',
                    'products': ['l1']},
            'tm5': {'inputs': 'LT52181092013069PFS00',
                    'products': ['l1']},
            'etm7': {'inputs': 'LE72181092013069PFS00',
                     'products': ['l1']},
            'oli8': {'inputs': 'LO82181092013069PFS00',
                     'products': ['l1']},
            'olitirs8': {'inputs': 'LC82181092013069PFS00',
                         'products': ['l1']},
            'projection': {'lonlat': None},
            'image_extents': {'north': 0.0002695,
                              'south': 0,
                              'east': 0.0002695,
                              'west': 0,
                              'units': 'dd'},
            'format': 'gtiff',
            'resampling_method': 'cc',
            'resize': {'pixel_size': 0.0002695,
                       'pixel_size_units': 'dd'},
            'plot_statistics': True}"""

    base = {'projection': {'lonlat': None},
            'image_extents': {'north': 0.002695,
                              'south': 0,
                              'east': 0.002695,
                              'west': 0,
                              'units': 'dd'},
            'format': 'gtiff',
            'resampling_method': 'cc',
            'resize': {'pixel_size': 0.0002695,
                       'pixel_size_units': 'dd'},
            'plot_statistics': True}

    sensor_acqids = {'.A2000072.h02v09.005.2008237032813': (['MOD09A1', 'MOD09GA', 'MOD09GQ', 'MOD09Q1',
                                                             'MYD09A1', 'MYD09GA', 'MYD09GQ', 'MYD09Q1',
                                                             'MOD13A1', 'MOD13A2', 'MOD13A3', 'MOD13Q1',
                                                             'MYD13A1', 'MYD13A2', 'MYD13A3', 'MYD13Q1'],
                                                            ['MOD09A1', 'MOD09GA', 'MOD09GQ', 'MOD09Q1',
                                                             'MYD09A1', 'MYD09GA', 'MYD09GQ', 'MYD09Q1',
                                                             'MOD13A1', 'MOD13A2', 'MOD13A3', 'MOD13Q1',
                                                             'MYD13A1', 'MYD13A2', 'MYD13A3', 'MYD13Q1']),
                     '2181092013069PFS00': (['LT4', 'LT5', 'LE7', 'LO8', 'LC8'],
                                            ['tm4', 'tm5', 'etm7', 'oli8', 'olitirs8'])}

    for acq in sensor_acqids:
        for prefix, label in zip(sensor_acqids[acq][0], sensor_acqids[acq][1]):
            base[label] = {'inputs': ['{}{}'.format(prefix, acq)],
                           'products': sn.instance('{}{}'.format(prefix, acq)).products}

    return base


class InvalidOrders(object):
    """
    Build a list of invalid orders and expected exception messages based on a
    given schema
    """
    def __init__(self, valid_order, schema, alt_fields=None, abbreviated=False):
        self.valid_order = valid_order
        self.schema = schema
        self.alt_fields = alt_fields

        self.abbreviated = abbreviated
        self.abbr = []

        self.invalid_list = []
        self.invalid_list.extend(self.build_invalid_list())

        self._error = None

    def __iter__(self):
        return iter(self.invalid_list)

    def build_exception(self, desc, value, fieldname, exctype=validator.FieldValidationError, path='', **params):
        """
        Build the expected error message for the failure

        This is directly modeled from validictory exception handling
        and uses the module's exception handlers
        """
        path = '<obj>.' + '.'.join(path)
        params['value'] = value
        params['fieldname'] = fieldname
        message = desc.format(**params)
        err = ''

        if exctype == validator.FieldValidationError:
            # err = "Value {!r} for field '{}' {}".format(value, path, message)
            err = validator.FieldValidationError(message, fieldname, value, path)
        elif exctype == validator.DependencyValidationError:
            # err = message
            err = exctype(message)
            err.fieldname = fieldname
            err.path = path
        elif exctype == validator.RequiredFieldValidationError:
            # err = message
            err = exctype(message)
            err.fieldname = fieldname
            err.path = path
        elif exctype == validator.SchemaError:
            err = exctype(message)

        # exc = validator.MultipleValidationError([err])
        exc = err

        return exc

    def build_invalid_list(self, path=None):
        """
        Recursively move through the base order and the validation schema

        Call invalidator methods based on the schema to build a list of invalid
        orders and their expected error messages to be returned
        """

        if not path:
            path = tuple()

        results = []

        sch_base = self.schema
        base = self.valid_order
        for key in path:
            sch_base = sch_base['properties'][key]
            base = base[key]

        if not path and 'oneormoreobjects' in sch_base:
            constr = sch_base['oneormoreobjects']
            results.extend(self.invalidate_oneormoreobjects(constr, path))

        for key, val in base.items():
            constraints = sch_base['properties'][key]
            mapping = path + (key,)

            for constr_type, constr in constraints.items():
                if self.abbreviated and constr_type in self.abbr:
                    continue
                elif self.abbreviated:
                    self.abbr.append(constr_type)

                invalidatorname = 'invalidate_' + constr_type

                try:
                    invalidator = getattr(self, invalidatorname, None)
                except:
                    raise Exception('{} has no associated testing'.format(constr_type))

                if not invalidator:
                    raise Exception('{} has no associated testing'.format(constr_type))

                results.extend(invalidator(constr, mapping))

            if constraints['type'] == 'object':
                results.extend(self.build_invalid_list(mapping))

        return results

    def invalidate_type(self, val_type, mapping):
        """
        Change the variable type
        """
        order = copy.deepcopy(self.valid_order)
        results = []
        test_vals = []

        if val_type == 'string':
            test_vals.append(9999)

        elif val_type == 'integer':
            test_vals.append('NOT A NUMBER')
            test_vals.append(1.1)

        elif val_type == 'number':
            test_vals.append('NOT A NUMBER')

        elif val_type == 'boolean':
            test_vals.append('NOT A BOOL')
            test_vals.append(2)
            test_vals.append(-1)

        elif val_type == 'object':
            test_vals.append('NOT A DICTIONARY')

        elif val_type == 'array':
            test_vals.append('NOT A LIST')

        elif val_type == 'null':
            test_vals.append('NOT NONE')

        elif val_type == 'any':
            pass

        else:
            raise Exception('{} constraint not accounted for in testing'.format(val_type))

        for val in test_vals:
            exc = self.build_exception('is not of type {fieldtype}', val, mapping[-1],
                                       path=mapping, fieldtype=val_type)
            upd = self.build_update_dict(mapping, val)
            results.append((self.update_dict(order, upd), 'type', exc))

        return results

    def invalidate_properties(self, val_type, mapping):
        """
        Used internally by validictory

        Tested through other methods
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        return results

    def invalidate_dependencies(self, dependency, mapping):
        """
        Remove dependencies, one at a time
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        for dep in dependency:
            path = mapping[:-1] + (dep,)
            # noinspection PyTypeChecker
            exc = self.build_exception("Field '{dependency}' is required by field '{fieldname}'", None,
                                       mapping[-1], dependency=dep, path=mapping,
                                       exctype=validator.DependencyValidationError)
            results.append((self.delete_key_loc(order, path), 'dependencies', exc))

        return results

    def invalidate_enum(self, enums, mapping):
        """
        Add a value not covered in the enum list
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        inv = 'NOT VALID ENUM'

        exc = self.build_exception("is not in the enumeration: {options!r}", inv, mapping[-1],
                                   path=mapping, options=enums)

        upd = self.build_update_dict(mapping, inv)
        results.append((self.update_dict(order, upd), 'enum', exc))
        return results

    def invalidate_required(self, req, mapping):
        """
        If the key is required, remove it
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        if req:
            # noinspection PyTypeChecker
            exc = self.build_exception("Required field '{fieldname}' is missing", None, mapping[-1],
                                       path=mapping, exctype=validator.RequiredFieldValidationError)
            results.append((self.delete_key_loc(order, mapping), 'required', exc))

        return results

    def invalidate_maximum(self, max_val, mapping):
        """
        Add one to the maximum allowed value
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        val = max_val + 1

        upd = self.build_update_dict(mapping, val)
        exc = self.build_exception("is greater than maximum value: {maximum}", val, mapping[-1],
                                   maximum=max_val, path=mapping)
        results.append((self.update_dict(order, upd), 'maximum', exc))
        return results

    def invalidate_minimum(self, min_val, mapping):
        """
        Subtract one from the minimum allowed value
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        val = min_val - 1

        upd = self.build_update_dict(mapping, val)
        exc = self.build_exception("is less than minimum value: {minimum}", val, mapping[-1],
                                   minimum=min_val, path=mapping)
        results.append((self.update_dict(order, upd), 'minimum', exc))
        return results

    def invalidate_uniqueItems(self, unique, mapping):
        """
        Add a duplicate entry into the list
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        if unique:
            base = order

            for key in mapping:
                base = base[key]

            base.append(base[0])

            upd = self.build_update_dict(mapping, base)
            exc = self.build_exception("is not unique", base[0], mapping[-1], path=mapping)
            results.append((self.update_dict(order, upd), 'uniqueItems', exc))

        return results

    def invalidate_items(self, val_type, mapping):
        """
        Used internally by validictory

        Subsets need to be tested through other methods
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        return results

    def invalidate_abs_rng(self, bounds, mapping):
        """
        Test out of bounds around the min and max allowed values
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        test_vals = [bounds[0] - 1, bounds[1] + 1, -bounds[0] + 1, -bounds[1] - 1]

        for val in test_vals:
            upd = self.build_update_dict(mapping, val)
            exc = self.build_exception('Absolute value must fall between {} and {}'.format(bounds[0], bounds[1]),
                                       val, mapping[-1], path=mapping)
            results.append((self.update_dict(order, upd), 'abs_rng', exc))

        return results

    def invalidate_single_obj(self, val_type, mapping):
        order = copy.deepcopy(self.valid_order)
        results = []
        # Needs to append a valid structure
        # Mainly pertains to the projection structure

        return results

    def invalidate_enum_keys(self, keys, mapping):
        """
        Append a dictionary with a key that is not in the
        enum list
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        inv_key = {'INVALID KEY': 'something'}

        upd = self.build_update_dict(mapping, inv_key)
        exc = self.build_exception('Unknown key: Allowed keys {}'.format(keys),
                                   'INVALID KEY', mapping[-1], path=mapping)
        results.append((self.update_dict(order, upd), 'enum_keys', exc))
        return results

    def invalidate_extents(self, max_pixels, mapping):
        # This is deeply tied into resize options as well
        order = copy.deepcopy(self.valid_order)
        results = []

        ext = {'north': 0,
               'south': 0,
               'east': 0,
               'west': 0,
               'units': 'dd'}

        # max pixels + 1 by keeping one of the dimensions = 1
        dd_ext = {'west': 0,
                  'east': (max_pixels + 1) * 0.0002695,
                  'south': 0,
                  'north': 0.0002695,
                  'units': 'dd'}

        m_ext = {'west': 0,
                 'east': (max_pixels + 1) * 30,
                 'south': 0,
                 'north': 30,
                 'units': 'meters'}

        order.pop('resize')

        if 'lonlat' in order['projection']:
            upd = {'image_extents': {'units': 'meters'}}
            exc = self.build_exception('must be "dd" for projection "lonlat"', 'meters', mapping[-1],
                                       path=mapping)
            results.append((self.update_dict(order, upd), 'extents', exc))
        else:
            upd = {'image_extents': m_ext}
            exc = self.build_exception(': pixel count value is greater than maximum size of {} pixels'.format(max_pixels),
                                       max_pixels + 1, mapping[-1], path=mapping)
            results.append((self.update_dict(order, upd), 'extents', exc))

        upd = {'image_extents': dd_ext}
        exc = self.build_exception(': pixel count value is greater than maximum size of {} pixels'.format(max_pixels),
                                   max_pixels + 1, mapping[-1], path=mapping)
        results.append((self.update_dict(order, upd), 'extents', exc))

        upd = {'image_extents': ext}
        exc = self.build_exception(': pixel count value falls below acceptable threshold, check extent parameters',
                                   0, mapping[-1], path=mapping)
        results.append((self.update_dict(order, upd), 'extents', exc))

        return results

    def invalidate_ps_dd_rng(self, rng, mapping):
        """
        Set values outside of the valid range
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        test_vals = [rng[0] - 1, rng[1] + 1]

        for val in test_vals:
            upd = self.build_update_dict(mapping[:-1], {'pixel_size': val, 'pixel_size_units': 'dd'})
            exc = self.build_exception('Value must fall between {} and {}'.format(rng[0], rng[1]),
                                       val, mapping[-1], path=mapping)
            results.append((self.update_dict(order, upd), 'ps_dd_rng', exc))

        return results

    def invalidate_ps_meter_rng(self, rng, mapping):
        """
        Set values outside of the valid range
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        if 'lonlat' in order['projection']:
            return results

        test_vals = [rng[0] - 1, rng[1] + 1]

        for val in test_vals:
            upd = self.build_update_dict(mapping[:-1], {'pixel_size': val, 'pixel_size_units': 'meters'})
            exc = self.build_exception('Value must fall between {} and {}'.format(rng[0], rng[1]),
                                       val, mapping[-1], path=mapping)
            results.append((self.update_dict(order, upd), 'ps_meter_rng', exc))

        return results

    def invalidate_role_restricted(self, restr, mapping):
        """
        If role base restrictions are on, add a restricted value to the list
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        if restr:
            prods = order
            for key in mapping:
                prods = prods[key]

            prods.append('restricted_prod')

            upd = self.build_update_dict(mapping, prods)
            exc = self.build_exception('The requested product(s) is not available at this time',
                                       ['restricted_prod'], mapping[-1], path=mapping)

            results.append((self.update_dict(order, upd), 'role_restricted', exc))

        return results

    def invalidate_oneormoreobjects(self, keys, mapping):
        """
        Remove any matching keys, so that nothing matches
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        loc = order
        for key in mapping:
            loc = loc[key]

        for key in keys:
            order = self.delete_key_loc(order, mapping + (key,))

        exc = self.build_exception('No requests for products were submitted', None, None, path=mapping,
                                   exctype=validator.RequiredFieldValidationError)

        results.append((order, 'oneormoreobjects', exc))

        return results

    def invalidate_set_ItemCount(self, (count_key, max_val), mapping):
        """
        Used internally for setting max number of items on arrays, not touched by users
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        return results

    def invalidate_ItemCount(self, count_key, mapping):
        """
        Increase the number of items in an array to exceed a set maximum
        """
        order = copy.deepcopy(self.valid_order)
        results = []

        max_val = 0
        # Need to locate the max value setting in the schema
        for key, val in self.schema.items():
            if key == 'set_ItemCount' and self.schema[key][0] == count_key:
                max_val = self.schema[key][1]
                break

        base = order
        for key in mapping:
            base = base[key]

        base.extend([base[0]] * max_val)

        upd = self.build_update_dict(mapping, base)
        exc = self.build_exception('Count exceeds size limit of {max} for {key}', None, None,
                                    exctype=validator.DependencyValidationError, max=max_val, key=key)
        results.append((self.update_dict(order, upd), 'ItemCount', exc))

        return results

    def update_dict(self, old, new):
        """
        Update a nested dictionary value following along a defined key path
        """
        ret = copy.deepcopy(old)

        for key, val in new.items():
            if isinstance(val, collections.Mapping):
                ret[key] = self.update_dict(ret[key], val)
            else:
                ret[key] = new[key]
        return ret

    def build_update_dict(self, path, val):
        """
        Build a new nested dictionary following a series of keys
        with a an endpoint value
        """
        ret = {}

        if len(path) > 1:
            ret[path[0]] = self.build_update_dict(path[1:], val)
        elif len(path) == 1:
            ret[path[0]] = val

        return ret

    def delete_key_loc(self, old, path):
        """
        Delete a key from a nested dictionary
        """
        ret = copy.deepcopy(old)

        if len(path) > 1:
            ret[path[0]] = self.delete_key_loc(ret[path[0]], path[1:])
        elif len(path) == 1:
            ret.pop(path[0], None)

        return ret
