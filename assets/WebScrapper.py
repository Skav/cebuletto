import json
from assets.CustomErrors import ShopsNotSet, ProductsNotSet
from decimal import Decimal
from queue import Queue, Empty
from assets.DTO.ProductData import ProductData
from assets.ScrapperThread import ScrapperThread



class WebScrapper:
    def __init__(self, data):
        self.__products_list = data['products']
        self.__shops_list = data['shops']
        self.__reverse_sort = True if data['order'] == 'asc' else False
        self.__config = self.__load_json("config")
        self.__shops_info = self.__load_json("shops_info")
        self.__shops_structure = self.__load_json("shops_structure")
        self.__result = Queue()
        self.__jobs = Queue()
        self.__errors = Queue()
        self.__threads = []

    def __load_json(self, name):
        try:
            with open('json/{}.json'.format(name)) as f:
                return json.load(f)
        except Exception as e:
            raise e

    def find_products(self, sort=True):
        try:
            self.__add_tasks_to_jobs()
            self.__init_threads()
            self.__wait_for_threads()
            results = self.__convert_to_dict()

            if sort:
                return self.__sort_products_by_price(results)
            return results
        except Exception as e:
            raise e

    def __add_tasks_to_jobs(self):
        if not self.__shops_list:
            raise ShopsNotSet
        if not self.__products_list:
            raise ProductsNotSet

        for product in self.__products_list:
            for shop in self.__shops_list:
                self.__jobs.put(ProductData(shop, product, self.__shops_structure[shop],
                                            self.__shops_info[shop]))

    def __init_threads(self):
        for i in range(self.__config["max_pages"]):
            if not self.__jobs.qsize() > 0:
                break
            self.__threads.append(ScrapperThread(self.__errors, self.__jobs, self.__result, self.__config, self.__shops_info))
            self.__threads[i].start()

    def __wait_for_threads(self):
        for thread in self.__threads:
            thread.join()

        try:
            errors = self.__errors.get(block=False)
        except Empty:
            pass
        else:
            raise errors

    def __convert_to_dict(self):
        try:
            products_keys = list()
            products_list = {}

            for products in self.__result.queue:
                key = list(products.keys())[0]
                if key not in products_keys:
                    products_keys.append(key)
                    products_list[key] = {}

            for products in self.__result.queue:
                for key in products_keys:
                    if key in products.keys():
                        shop_name = list(products[key].keys())[0]
                        products_list[key][shop_name] = products[key][shop_name]
                        break
            return products_list
        except Exception as e:
            print("Error while convert products to dict: {}".format(e))
            raise e

    def __sort_products_by_price(self, products_list):
        try:
            for item in products_list.keys():
                for shop in products_list[item].keys():
                    products_list[item][shop] = {k: v for k, v in sorted(products_list[item][shop].items(),
                                                 key=lambda x: Decimal(x[1]["price"]) if not x[1] == "Brak" else x[1],
                                                 reverse=self.__reverse_sort)}
            return products_list
        except Exception as e:
            raise e

    @staticmethod
    def get_shops():
        with open('json/shops_info.json') as f:
            shops = json.load(f)
            return list(shops.keys())
