""" Holds domain objects for orders and the items attached to them """

class Order(object):
    """ x """

    def __init__(self, username, input_products, output_products,
                 projection=None, pixel_size=None, image_extents=None,
                 resampling_method=None, output_format=None):
        """
        Args:
        username (str): User this order is for
        input_products (list): input product ids to process
        output_products (list): conventionalized output products
        projection (dict): dictionary of projection information
        pixel_size (float): requested output pixel size
        pixel_size_units (str): meters or dd
        image_extents (dict): north, south, east, west boundaries as floats
        image_extents_units (str): meters or dd
        resampling_method (str): nn, bi or cc
        output_format (str): gtiff, envi, hdf-eos2, or envi-bip
        """
        self.username = username
        self.input_products = input_products
        self.output_products = output_products
        self.projection = projection
        self.pixel_size = pixel_size
        self.image_extents = image_extents
        self.resampling_method = resampling_method
        self.output_format = output_format
        self.validate()

    def to_dict(self):
        """ x """
        pass

    @staticmethod
    def from_dict(dadsf):
        """ x """
        pass

    def __repr__(self):
        pass

    def validate(self):
        """ checks that this object was constructed correctly

        Raises:
            ValidationException if incorrect parameters specified
        """
        #registry.validation.validate(self)
        pass
