import json
from pathlib import Path
from assets.CustomErrors import SearchDataNotSet
from decimal import Decimal
from queue import Queue, Empty
from assets.DTO.ProductData import ProductData
from assets.ScrapperThread import ScrapperThread
from os import getenv
from assets.database.Interfaces.ProductsTagsInterface import ProductsTagsInterface
from assets.database.Interfaces.TagsToProductsInterface import TagsToProductsInterface
from assets.database.Interfaces.ShopsInterface import ShopsInterface
from datetime import datetime

class WebScrapper:
    def __init__(self, data):
        self.__products = data['products']
        self.__shops = data['shops']
        self.__search_data = {k: data['products'][:] for k in data['shops']}
        self.__reverse_sort = True if data['order'] == 'asc' else False
        self.__config = {
            "max_pages": int(getenv('SCRAPPER_MAX_PAGES')),
            "web_browser": getenv('SCRAPPER_WEB_BROWSER'),
            "path_to_browser_driver": getenv('SCRAPPER_PATH_TO_BROWSER_DRIVER')
        }
        self.__shops_info = self.__load_json("shops_info")
        self.__shops_structure = self.__load_json("shops_structure")
        self.__result = Queue()
        self.__jobs = Queue()
        self.__errors = Queue()
        self.__threads = []

    def __load_json(self, name):
        try:
            with open(Path(__file__).parent / '../json/{}.json'.format(name)) as f:
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

    # TODO:
    # Zmienic zasade wyszukiwania produktow: dict z sklepem i produktami ktore maja byc w nim znalezione
    # Dokonczyc wyszukiwnaie produktow w bazie
    # Przefiltrowanie produktow i sklepow w ktorych znaleziono dane dane, w celu unikniecia scrappowania

    def __get_products_from_database(self):
        existings_tags = [x for x in self.__products if ProductsTagsInterface.check_tag_exist(x)]
        shops_info = self.__get_shops_with_id()
        self.__search_data = {k: [v for v in self.__products if v not in existings_tags] for k in self.__shops}

        for shop in self.__shops:
            for tag in existings_tags:
                products_data = TagsToProductsInterface.get_products_by_tag_and_shop_id(shops_info[shop], tag)
                products_list = {}
                for product in products_data:
                    if self.__check_hours_since_update(product['lastUpdate'] > getenv("SCRAPPER_TIME_INTERVAL_BETWEEN_SEARCH")):
                        if shop in self.__search_data.keys():
                            self.__search_data[shop].append(product)
                        else:
                            self.__search_data[shop] = [product]
                        break

                    products_list[tag][shop] = {'price': product["price"], 'discount_price': product["discountPrice"],
                                                'link': product[''], 'image_url': product, 'available': product}





    def __get_products_by_name_and_shop_id(self, product, shop_id):
        return TagsToProductsInterface.get_products_by_tag_and_shop_id(product, shop_id)

    def __get_shops_with_id(self):
        shops = ShopsInterface.get_all_shops()
        return {x["name"]: x["idShop"] for x in shops}

    def __check_hours_since_update(self, update_time: datetime):
        duration = datetime.now() - update_time

        return divmod(duration, 3600)[0]

    def __add_tasks_to_jobs(self):
        if not self.__search_data:
            raise SearchDataNotSet

        for shop, products in self.__search_data.items():
            for product in products:
                self.__jobs.put(ProductData(shop, product, self.__shops_structure[shop], self.__shops_info[shop]))

    def __init_threads(self):
        for i in range(self.__config["max_pages"]):
            if not self.__jobs.qsize() > 0:
                break
            self.__threads.append(
                ScrapperThread(self.__errors, self.__jobs, self.__result, self.__config, self.__shops_info))
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
        with open(Path(__file__).parent / '../json/shops_info.json') as f:
            shops = json.load(f)
            return list(shops.keys())
