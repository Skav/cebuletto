class WebDriverNotFound(Exception):
    def __init__(self, web_browser):
        super().__init__("Web driver for {} not found".format(web_browser))


class ShopsNotSet(Exception):
    def __init__(self):
        super().__init__("Shops are not set")


class ProductsNotSet(Exception):
    def __init__(self):
        super().__init__("Products are not set")


class SearchDataNotSet(Exception):
    def __init__(self):
        super().__init__("Search data are not set")


class SerializerError(Exception):
    def __init__(self, message):
        super().__init__(message)