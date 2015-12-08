import registry

def place_order(username, input_products, output_products,
                projection=None, pixel_size=None, pixel_size_units=None,
                image_extents=None, image_extents_units=None,
                resampling_method=None, output_format=None):

    # perform validation, raises ValidationException
    registry.validation.validate(username,
                                 input_products,
                                 output_products,
                                 projection, 
                                 pixel_size,
                                 pixel_size_units,
                                 image_extents,
                                 image_extents_units,
                                 resampling_method,
                                 output_format)

                                 
    # performs inventory check, raises InventoryException
    registry.inventory.check(username,
                             input_products,
                             output_products,
                             projection, 
                             pixel_size,
                             pixel_size_units,
                             image_extents,
                             image_extents_units,
                             resampling_method,
                             output_format)

    # track metrics
    registry.metrics.collect(username,
                             input_products,
                             output_products,
                             projection, 
                             pixel_size,
                             pixel_size_units,
                             image_extents,
                             image_extents_units,
                             resampling_method,
                             output_format)

    # capture the order
    return registry.ordering.place_order(username,
                                         input_products,
                                         output_products,
                                         projection, 
                                         pixel_size,
                                         pixel_size_units,
                                         image_extents,
                                         image_extents_units,
                                         resampling_method,
                                         output_format)


def list_orders(username_or_email):
    return registry.ordering.list_orders(username_or_email)


def view_order(username, orderid):
    return registry.ordering.view_order(username, orderid)
