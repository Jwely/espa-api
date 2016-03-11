from api.domain.order import Order
from api.domain import sensor


def convert_options(opts):
    """
    We have to map to the old way of passing an order to the back end
    until the back end is ready to process the new format

    :param sceneid: scene to be passed back
    :param opts: order associated with the scene
    :return: dict
    """
    ret = {}

    new_prods = opts['products']

    ret.update(convert_product_names(new_prods))
    ret.update(convert_projection(opts))
    ret.update(convert_resize(opts))
    ret.update(convert_subset(opts))

    if 'format' in opts:
        ret['output_format'] = opts['format']
    else:
        ret.update(Order.get_default_output_format())

    if 'resampling_method' in opts:
        ret['resample_method'] = opts['resampling_method']
    else:
        ret.update(Order.get_default_resample_options())

    return ret


def convert_product_names(request_prods):
    ret = Order.get_default_product_options()

    if 'l1' in request_prods:
        ret['include_source_data'] = True
    if 'stats' in request_prods:
        ret['include_statistics'] = True
    if 'source_metadata' in request_prods:
        ret['include_source_metadata'] = True
    # if 'toa' in new_prods:
    #     defaults['include_customized_source_data'] = True
    if 'toa' in request_prods:
        ret['include_sr_toa'] = True
    if 'bt' in request_prods:
        ret['include_sr_thermal'] = True
    if 'sr' in request_prods:
        ret['include_sr'] = True
    if 'swe' in request_prods:
        ret['include_dswe'] = True
    # if 'toa' in new_prods:
    #     defaults['include_sr_browse'] = True
    if 'sr_ndvi' in request_prods:
        ret['include_sr_ndvi'] = True
    if 'sr_ndmi' in request_prods:
        ret['include_sr_ndmi'] = True
    if 'sr_nbr' in request_prods:
        ret['include_sr_nbr'] = True
    if 'sr_nbr2' in request_prods:
        ret['include_sr_nbr2'] = True
    if 'sr_savi' in request_prods:
        ret['include_sr_savi'] = True
    if 'sr_msavi' in request_prods:
        ret['include_sr_msavi'] = True
    if 'sr_evi' in request_prods:
        ret['include_sr_evi'] = True
    if 'lst' in request_prods:
        ret['include_lst'] = True
    # if 'toa' in new_prods:
    #     defaults['include_solr_index'] = True
    if 'cloud' in request_prods:
        ret['include_cfmask'] = True

    return ret


def convert_projection(opts):
    ret = Order.get_default_projection_options()

    if 'projection' in opts:
        proj = opts['projection']
        proj_name = proj.keys()[0]

        ret['reproject'] = True
        ret['target_projection'] = proj_name

        for key in proj:
            if key in ret:
                ret[key] = proj[key]

    return ret


def convert_subset(opts):
    ret = Order.get_default_subset_options()

    if 'image_extents' in opts:
        ext_opts = opts['image_extents']

        ret['image_extents'] = True
        ret['image_extents_units'] = ext_opts['units']
        ret['minx'] = ext_opts['west']
        ret['miny'] = ext_opts['south']
        ret['maxx'] = ext_opts['east']
        ret['maxy'] = ext_opts['north']

    return ret


def convert_resize(opts):
    ret = Order.get_default_resize_options()

    if 'resize' in opts:
        res_opts = opts['resize']

        ret['resize'] = True
        ret['pixel_size'] = res_opts['pixel_size']
        ret['pixel_size_units'] = res_opts['pixel_size_units']

    return ret
