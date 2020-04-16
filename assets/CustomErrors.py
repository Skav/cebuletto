class WebDriverNotFound(Exception):
    def __init__(self, web_browser):
        super().__init__("Web driver for {} not found".format(web_browser))

