import json
import re


class Serializer:
    def __init__(self, data):
        self.__request_data = data
        self.data = None
        self.__valid = True
        self.errors = ""
        self.__shops_info = self.__load_file()

    def __load_file(self):
        with open("json/shops_info.json") as f:
            return json.load(f)

    def serialize_data(self):
        self.__check_request_keys()

        if not self.__valid:
            return False

        products = self.__request_data["products_list"]
        shops = self.__request_data["shops_list"]
        clear_products = [re.sub('[^\d+\w+\-_ ]', '', x).strip() for x in products]
        clear_shops = [re.sub('[^\d+a-zA-Z.\- ]', '', x).strip() for x in shops]
        products = [x.replace('-', ' ').replace('_', ' ') for x in clear_products if x]
        shops = [x for x in clear_shops if x]

        if not products:
            self.__create_error("There is not products in products_list")
        if not shops:
            self.__create_error("There is not shops in shops_list")

        if not self.__valid:
            return False

        unsupported_shops = [shop for shop in shops if shop not in self.__shops_info.keys()]

        if unsupported_shops:
            self.__create_error("This shop(s) are unsupported by application: {}".format(', '.join(unsupported_shops)))
            return False

        self.data = {"products": products,
                     "shops": shops,
                     "order": self.__request_data['order']}

    def __check_request_keys(self):
        if "products_list" not in self.__request_data:
            self.__create_error("product_list is not set")
        if "shops_list" not in self.__request_data:
            self.__create_error("shop_list is not set")
        if "order" in self.__request_data:
            if not self.__request_data['order'] in ('asc', 'desc'):
                self.__create_error("incorrect order value")
        else:
            self.__request_data['order'] = 'desc'

    def __create_error(self, message):
        self.__valid = False
        self.errors = "{}; {}".format(self.errors, message) if self.errors else message

    def is_valid(self):
        return self.__valid





