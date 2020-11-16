from json import load
from re import sub
from .BaseSerializer import BaseSerializer


class RequestSerializer(BaseSerializer):
    def __init__(self, data):
        super().__init__()
        self.__request_data = data
        self.data = None
        self.__shops_info = self.__load_file()
        self.__serialize_data()

    def __load_file(self):
        with open("json/shops_info.json") as f:
            return load(f)

    def __serialize_data(self):

        if not self.__are_request_keys_correct():
            return False

        products = self.__request_data["products_list"]
        shops = self.__request_data["shops_list"]
        clear_products = [sub('[^\d+\w+\-_\' ]', '', x).strip() for x in products]
        clear_shops = [sub('[^\d+a-zA-Z.\- ]', '', x).strip() for x in shops]
        products = [x.replace('-', ' ').replace('_', ' ') for x in clear_products if x]
        shops = [x for x in clear_shops if x]

        if not products:
            self._set_error("There is not products in products_list")
        if not shops:
            self._set_error("There is not shops in shops_list")

        if not self.is_valid:
            return False

        unsupported_shops = [shop for shop in shops if shop not in self.__shops_info.keys()]

        if unsupported_shops:
            self._set_error("This shop(s) are unsupported by application: {}".format(', '.join(unsupported_shops)))
            return False

        self.data = {"products": products,
                     "shops": shops,
                     "order": self.__request_data['order']}

    def __are_request_keys_correct(self):
        if "products_list" not in self.__request_data:
            self._set_error("products_list is not set")
        if "shops_list" not in self.__request_data:
            self._set_error("shops_list is not set")
        if "order" in self.__request_data:
            if not self.__request_data['order'] in ('asc', 'desc'):
                self._set_error("incorrect order value")
        else:
            self.__request_data['order'] = 'desc'

        return True if self.is_valid else False




