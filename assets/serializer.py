import json
import re


class Serializer:
    def __init__(self, data):
        self.__request_data = data
        self.__data = None
        self.__valid = True
        self.__validation_message = ""
        self.__shops_info = self.__load_file()

    def __load_file(self):
        with open("json/shops_info.json") as f:
            return json.load(f)

    def serialize_data(self):
        if "products_list" not in self.__request_data:
            self.__valid = False
            self.__validation_message = "products_list is not set"
            return False
        if "shops_list" not in self.__request_data:
            self.__valid = False
            self.__validation_message = "shop_list is not set"
            return False

        products = self.__request_data["products_list"]
        shops = self.__request_data["shops_list"]
        clear_products = [re.sub('[^\d+\w+\-_ ]', '', x).strip() for x in products]
        clear_shops = [re.sub('[^\d+a-zA-Z.\- ]', '', x).strip() for x in shops]
        products = [x.replace('-', ' ').replace('_', ' ') for x in clear_products if x]
        shops = [x for x in clear_shops if x]

        if not products:
            self.__valid = False
            self.__validation_message = "There is not products in prodcuts_list"
            return False
        if not shops:
            self.__valid = False
            self.__validation_message = "There is not shops in shops_list"
            return False

        unsupported_shops = []
        for shop in shops:
            if shop not in self.__shops_info.keys():
                unsupported_shops.append(shop)

        if unsupported_shops:
            self.__valid = False
            self.__validation_message = "This shop(s) are unsupported by application: {}".format(', '.join(unsupported_shops))

        self.__data = {"products": products,
                       "shops": shops}

    def is_valid(self):
        return self.__valid

    def get_errors(self):
        return self.__validation_message

    def get_data(self):
        return self.__data





