import json
from assets.CustomErrors import WebDriverNotFound
from decimal import Decimal
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup
from selenium import webdriver
from re import sub

class shopsInfo:
    @staticmethod
    def get_shops():
        try:
            with open('json/shops_info.json') as f:
                shops = json.load(f)
                return list(shops.keys())
        except Exception as e:
            print("Loading file error: {}".format(e))
            raise e


class WebScrapper:
    def __init__(self, products):
        self.__products_list = products
        self.__config = self.__load_json("config")
        self.__shops_info = self.__load_json("shops_info")
        self.__shops_structure = self.__load_json("shops_structure")
        self.__browser_options = self.__set_browser_options(self.__config["web_browser"])
        self.__result = Queue()
        self.__jobs = Queue()
        self.__threads = []

    def __load_json(self, name):
        try:
            with open('json/{}.json'.format(name)) as f:
                return json.load(f)
        except Exception as e:
            print("Loading file error: {}".format(e))
            raise e

    def __set_browser_options(self, web_browser):
        if web_browser == "Chrome":
            browser_options = webdriver.ChromeOptions()
        elif web_browser == "Firefox":
            browser_options = webdriver.FirefoxOptions()
        else:
            raise WebDriverNotFound

        browser_options.add_argument('headless')
        return browser_options

    def __get_products(self):
        try:
            while not self.__jobs.empty():
                list_of_products = {}

                search_data = self.__jobs.get().split(';')
                shop = search_data[0].strip()
                product_name = search_data[1].strip()
                shop_products = {product_name: {}}

                print(shop, " ", product_name)

                shop_struct = self.__shops_structure[shop]
                product_name_keys = product_name.lower().split(" ")
                product_separated_name = product_name.replace(" ", self.__shops_info[shop]["separator"])
                url = "{}{}".format(self.__shops_info[shop]["request_url"], product_separated_name)

                if "extra_requests" in self.__shops_info[shop]:
                    url = url+"{}".format(self.__shops_info[shop]["extra_requests"])
                driver = self.__set_web_driver()
                soup = self.__get_page(url, driver)
                products = self.__get_products_list(soup["source"], shop_struct)

                if not products:
                    results = self.__try_find_data_on_product_page(soup, shop, shop_struct, product_name_keys)
                    if not results:
                        self.__no_product_in_shop(shop_products, product_name, shop)
                        continue
                    shop_products[product_name][shop] = results
                    self.__result.put(shop_products)
                    self.__jobs.task_done()
                    continue

                for product in products:
                    name = self.__get_name(product, product_name_keys, shop_struct)
                    if not name:
                        continue

                    link = self.__get_link(product, shop_struct, shop)
                    price = self.__get_price(product, shop_struct)
                    available = False if not price else self.__is_product_available(product, shop_struct)

                    if not price:
                        price = {"regular": "0", "discount": "0"}

                    list_of_products[name] = {'price': price["regular"], 'discount_price': price["discount"],
                                              'link': link, 'available': available}

                if not list_of_products:
                    list_of_products = self.__try_find_data_on_product_page(soup, shop, shop_struct, product_name_keys)
                    if not list_of_products:
                        self.__no_product_in_shop(shop_products, product_name, shop)
                        continue
                shop_products[product_name][shop] = list_of_products
                self.__result.put(shop_products)
                self.__jobs.task_done()
        except Exception as e:
            print("Error in main function: {}".format(e))
            raise e

    def __try_find_data_on_product_page(self, soup, shop, shop_struct, product_name_keys):
        if not self.__shops_info[shop]["redirect_to_product_page"]:
            return False
        product_page_struct = shop_struct["single_product_page"]

        name = self.__get_name(soup["source"], product_name_keys, product_page_struct)
        if not name:
            return False

        price = self.__get_price(soup["source"], product_page_struct)
        link = soup["url"]
        available = False if not price else self.__is_product_available(soup["source"], product_page_struct)

        if not price:
            price = {"regular": "0", "discount": "0"}

        return {name: {'price': price["regular"], 'discount_price': price["discount"], 'link': link,
                       'available': available}}


    def __no_product_in_shop(self, shop_products, product_name, shop):
        shop_products[product_name][shop] = {product_name: "Brak"}
        self.__result.put(shop_products)
        self.__jobs.task_done()

    def __is_product_available(self, product, shop_struct):
        if "available" in shop_struct.keys():
            product_available = product.find(shop_struct["available"]["type"],
                                             attrs=shop_struct["available"]["attrs"])
            if not product_available:
                return True

            if "not_available_message" in shop_struct["available"].keys():
                if "child_type" in shop_struct["available"].keys():
                    product_available = product_available.find(shop_struct["available"]["child_type"],
                                                               attrs=shop_struct["available"]["child_attrs"])

                if product_available.text.lower() == shop_struct["available"]["not_available_message"].lower():
                    return False
        return True

    def __set_web_driver(self):
        if self.__config["web_browser"] == "Chrome":
            return webdriver.Chrome(options=self.__browser_options)
        elif self.__config["web_browser"] == "Firefox":
            return webdriver.Firefox(options=self.__browser_options)
        else:
            raise WebDriverNotFound

    def __get_page(self, url, driver):
        try:
            driver.get(url)
            return {"url": driver.current_url, "source": BeautifulSoup(driver.page_source, 'html.parser')}
        except Exception as e:
            print("Error while getting page: {}".format(e))
            raise e

    def __get_products_list(self, soup, shop_struct):
        try:
            products_list = soup.find(shop_struct["all_products_container"]["type"],
                                      attrs=shop_struct["all_products_container"]["attrs"])
            if not products_list:
                return False

            return products_list.find_all_next(shop_struct["products_container"]["type"],
                                               attrs=shop_struct["products_container"]["attrs"])
        except Exception as e:
            print("Error while getting products list: {}".format(e))
            raise e

    def __get_name(self, product, product_name_keys, shop_struct):
        try:
            name_container = product.find(shop_struct["product_name"]["type"],
                                          attrs=shop_struct["product_name"]["attrs"])

            if not name_container:
                return False

            if "child_type" in shop_struct["product_name"].keys():
                name_container = name_container.find(shop_struct["product_name"]["child_type"],
                                                     attrs=shop_struct["product_name"]["child_attrs"])

            name = name_container.text if name_container.text else name_container['title']

            if not all(x.lower() in name.lower() for x in product_name_keys):
                return False
            return name
        except Exception as e:
            print("Error while getting product name: {}".format(e))
            raise e

    def __get_link(self, product, shop_struct, key):
        try:
            if "child_type" in shop_struct["product_url"]:
                link_container = product.find(shop_struct["product_url"]["type"],
                                              attrs=shop_struct["product_url"]["attrs"])
                return link_container.find(shop_struct["product_url"]["child_type"],
                                           attrs=shop_struct["product_url"]["child_attrs"])['href']
            link = product.find(shop_struct["product_url"]["type"], attrs=shop_struct["product_url"]["attrs"])['href']

            if not self.__shops_info[key]["has_domain_in_link"]:
                link = "{}{}".format(self.__shops_info[key]["url"], link)

            return link
        except Exception as e:
            print('Error while getting product url: {}'.format(e))
            raise e

    def __get_price(self, product, shop_struct):
        try:
            discount_price = ""
            if "product_price_container" in shop_struct.keys():
                price_div = product.find(shop_struct["product_price_container"]["type"],
                                         attrs=shop_struct["product_price_container"]["attrs"])

                if not price_div:
                    return False

                regular_price = price_div.find(shop_struct["product_price"]["type"],
                                               attrs=shop_struct["product_price"]["attrs"])
                if regular_price and "child_type" in shop_struct["product_price"]:
                    regular_price = regular_price.find(shop_struct["product_price"]["child_type"],
                                                       attrs=shop_struct["product_price"]["child_attrs"])

                regular_price = regular_price.text if regular_price else None

                if not regular_price and "second_regular_price" in shop_struct.keys():
                    regular_price = price_div.find(shop_struct["second_regular_price"]["type"],
                                                   attrs=shop_struct["second_regular_price"]["attrs"])

                    if "child_type" in shop_struct["second_regular_price"]:
                        regular_price = regular_price.find(shop_struct["second_regular_price"]["child_type"],
                                                           attrs=shop_struct["second_regular_price"]["child_attrs"]).text
                    else:
                        regular_price = regular_price.text

                if "discount_price" in shop_struct.keys():
                    if price_div.find(shop_struct["discount_price"]["type"],
                                      attrs=shop_struct["discount_price"]["attrs"]):
                        discount_price = price_div.find(shop_struct["discount_price"]["type"],
                                                        attrs=shop_struct["discount_price"]["attrs"])

                        if "child_type" in shop_struct["discount_price"]:
                            discount_price = discount_price.find(shop_struct["discount_price"]["child_type"],
                                                                 attrs=shop_struct["discount_price"]["child_attrs"]).text
                        else:
                            discount_price = discount_price.text
            else:
                regular_price = product.find(shop_struct["product_price"]["type"],
                                             attrs=shop_struct["product_price"]["attrs"])

                if "child_type" in shop_struct["product_price"]:
                    regular_price = regular_price.find(shop_struct["product_price"]["child_type"],
                                                       attrs=shop_struct["product_price"]["child_attrs"])

                regular_price = regular_price.text if regular_price else None

                if not regular_price and "second_regular_price" in shop_struct.keys():
                    regular_price = product.find(shop_struct["second_regular_price"]["type"],
                                                 attrs=shop_struct["second_regular_price"]["attrs"])

                    if not regular_price:
                        return False
                    elif "child_type" in shop_struct["second_regular_price"]:
                        regular_price = regular_price.find(shop_struct["second_regular_price"]["child_type"],
                                                     attrs=shop_struct["second_regular_price"]["child_attrs"]).text
                    else:
                        regular_price = regular_price.text

                if "discount_price" in shop_struct.keys():
                    if product.find(shop_struct["discount_price"]["type"],
                                    attrs=shop_struct["discount_price"]["attrs"]):
                        discount_price = product.find(shop_struct["discount_price"]["type"],
                                                      attrs=shop_struct["discount_price"]["attrs"])

                        if "child_type" in shop_struct["discount_price"]:
                            discount_price = discount_price.find(shop_struct["discount_price"]["type"],
                                                                 attrs=shop_struct["discount_price"]["attrs"]).text
                        else:
                            discount_price = discount_price.text

            regular_price = sub('[^\d+.,]', '', regular_price).replace(',', '.')
            discount_price = sub('[^\d+.,]', '', discount_price).replace(',', '.')

            if regular_price[-1:] in (',', '.'):
                regular_price = regular_price[:-1]

            if discount_price[-1:] in ('.', ','):
                discount_price = discount_price[:-1]

            regular_price = Decimal(regular_price.replace(',', '.')) if regular_price else Decimal(0)
            discount_price = Decimal(discount_price.replace(',', '.')) if discount_price else Decimal(0)

            if regular_price == discount_price:
                discount_price = Decimal(0)

            return {"regular": str(regular_price), "discount": str(discount_price)}
        except Exception as e:
            print("Error while getting price: {}".format(e))
            raise e

    def find_products(self, shop_list=None):
        try:
            self.__add_tasks_to_jobs(shop_list)
            self.__init_threads()
            self.__wait_for_threads()

            return self.__convert_to_dict()
        except WebDriverNotFound as e:
            print("Web browser driver set in config file not found, please check your configuration file")
            raise e
        except Exception as e:
            raise e

    def __add_tasks_to_jobs(self, shop_list=None):
        try:
            shops = shop_list if shop_list else self.__shops_structure.keys()
            for product in self.__products_list:
                for shop in shops:
                    self.__jobs.put('{};{}'.format(shop, product))
        except Exception as e:
            print("Error while adding jobs to queue: {}".format(e))
            raise e

    def __wait_for_threads(self):
        try:
            for thread in self.__threads:
                thread.join()
        except Exception as e:
            print("Error while starting threads: {}".format(e))
            raise e

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

    def sort_products_by_price(self, products_list, reverse=False):
        try:
            for item in products_list.keys():
                for shop in products_list[item].keys():
                    products_list[item][shop] = {k: v for k, v in sorted(products_list[item][shop].items(),
                                                 key=lambda x: Decimal(x[1]["price"]) if not x[1] == "Brak" else x[1],
                                                 reverse=reverse)}
            return products_list
        except Exception as e:
            raise e

    def __init_threads(self):
        try:
            for i in range(self.__config["max_pages"]):
                if not self.__jobs.qsize() > 0:
                    break
                self.__threads.append(Thread(target=self.__get_products, daemon=True))
                self.__threads[i].start()
        except Exception as e:
            print("Error while init a threads: {}".format(e))
            raise e

    def __wait_for_threads(self):
        try:
            for thread in self.__threads:
                thread.join()
        except Exception as e:
            print("Error while joining threads: {}".format(e))
            raise e

    def get_shops_list(self):
        try:
            return list(self.__shops_info.keys())
        except Exception as e:
            print("Error while getting shops list: {}".format(e))
            raise e
