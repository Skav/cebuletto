class BaseSerializer:

    def __init__(self):
        self.errors = ''
        self.is_valid = True

    def _set_error(self, message):
        self.is_valid = False
        self.errors = "{}; {}".format(self.errors, message) if self.errors else message
