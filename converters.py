from werkzeug.routing import BaseConverter

# include the regex converter, needed in the blueprints
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
