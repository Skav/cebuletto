import json
from decimal import Decimal
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup
from selenium import webdriver
from re import sub


class webScrapper:
    def __init__(self, products):
        self.__products_list = products
        self.__config = self.__load_json("config")
        self.__shops_info = self.__load_json("shops_info")
        self.__shops_structure = self.__load_json("shops_structure")
        self.__browser_options = self.__set_browser_options(self.__config["web_browser"])
        self.__result = Queue()
        self.__jobs = Queue()
        self.__threads = []
        self.__add_tasks_to_jobs()

    def __load_json(self, name):
        try:
            with open('{}.json'.format(name)) as f:
                return json.load(f)
        except Exception as e:
            print("Loading file error: {}".format(e))

    def __set_browser_options(self, web_browser):
        try:
            browser = web_browser
            if browser == "Chrome":
                browser_options = webdriver.ChromeOptions()
            elif browser == "Firefox":
                browser_options = webdriver.FirefoxOptions()
            else:
                return False

            browser_options.add_argument('headless')
            return browser_options
        except Exception as e:
            print("Set browser options error: {}".format(e))

    def __add_tasks_to_jobs(self):
        try:
            for product in self.__products_list:
                for key in self.__shops_structure.keys():
                    self.__jobs.put('{};{}'.format(key, product))
        except Exception as e:
            print("Error while adding jobs to queue: {}".format(e))

    def __get_products(self):
        while not self.__jobs.empty():
            list_of_products = {}

            search_data = self.__jobs.get().split(';')
            key = search_data[0].strip()
            product_name = search_data[1].strip()

            shop_products = {product_name: {}}

            print(key, " ", product_name)

            shop_struct = self.__shops_structure[key]
            product_name_keys = product_name.lower().split(" ")
            product_separated_name = product_name.replace(" ", self.__shops_info[key]["separator"])
            url = "{}{}".format(self.__shops_info[key]["request_url"], product_separated_name)

            driver = self.__set_web_driver()
            if not driver:
                print("Webdriver does not exist!")
                return False
            soup = self.__get_page(url, driver)


            products = self.__get_products_list(soup, shop_struct)

            if not products:
                shop_products[product_name][key] = "Brak"
                self.__result.put(shop_products)
                self.__jobs.task_done()
                return False

            for product in products:
                name = self.__get_name(product, product_name_keys, shop_struct)
                if not name:
                    continue

                link = self.__get_link(product, shop_struct, key)
                price = self.__get_price(product, shop_struct)

                list_of_products[name] = {'price': price["regular"], 'discount_price': price["discount"], 'link': link}

            shop_products[product_name][key] = list_of_products
            self.__result.put(shop_products)
            self.__jobs.task_done()

    def __set_web_driver(self):
        try:
            if self.__config["web_browser"] == "Chrome":
                return webdriver.Chrome(options=self.__browser_options)
            elif self.__config["web_browser"] == "Firefox":
                return webdriver.Firefox(options=self.__browser_options)
            else:
                return False
        except Exception as e:
            print("Error while setting webdriver: {}".format(e))

    def __get_page(self, url, driver):
        driver.get(url)
        return BeautifulSoup(driver.page_source, 'html.parser')

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

    def __get_name(self, product, product_name_keys, shop_struct):
        try:
            name_container = product.find(shop_struct["product_name"]["type"],
                                          attrs=shop_struct["product_name"]["attrs"])

            if "child_type" in shop_struct["product_name"].keys():
                name_container = name_container.find(shop_struct["product_name"]["child_type"],
                                                     attrs=shop_struct["product_name"]["child_attrs"])

            name = name_container.text if name_container.text else name_container['title']

            if not all(x in name.lower() for x in product_name_keys):
                return False
            return name
        except Exception as e:
            print("Error while getting product name: {}".format(e))

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

    def __get_price(self, product, shop_struct):
        discount_price = ""
        if "product_price_container" in shop_struct.keys():
            price_div = product.find(shop_struct["product_price_container"]["type"],
                                     attrs=shop_struct["product_price_container"]["attrs"])
            regular_price = price_div.find(shop_struct["product_price"]["type"],
                                           attrs=shop_struct["product_price"]["attrs"])

            regular_price = regular_price.text if regular_price else None

            if not regular_price and "second_regular_price" in shop_struct.keys():
                regular_price = price_div.find(shop_struct["second_regular_price"]["type"],
                                               attrs=shop_struct["second_regular_price"]["attrs"]).text

            if "product_discount_price" in shop_struct.keys():
                if price_div.find(shop_struct["product_discount_price"]["type"],
                                  attrs=shop_struct["product_discount_price"]["attrs"]):
                    discount_price = price_div.find(shop_struct["product_discount_price"]["type"],
                                                    attrs=shop_struct["product_discount_price"]["attrs"]).text
        else:
            regular_price = product.find(shop_struct["product_price"]["type"],
                                         attrs=shop_struct["product_price"]["attrs"]).text

            if not regular_price and "second_regular_price" in shop_struct.keys():
                regular_price = product.find(shop_struct["second_regular_price"]["type"],
                                             attrs=shop_struct["second_regular_price"]["attrs"]).text

            if "product_discount_price" in shop_struct.keys():
                if product.find(shop_struct["product_discount_price"]["type"],
                                attrs=shop_struct["product_discount_price"]["attrs"]):
                    discount_price = product.find(shop_struct["product_discount_price"]["type"],
                                                  attrs=shop_struct["product_discount_price"]["attrs"]).text

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

        return {"regular": regular_price, "discount": discount_price}

    def __wait_for_threads(self):
        for thread in self.__threads:
            thread.join()

    def find_products(self):
        self.__init_threads()
        self.__wait_for_threads()

        return self.__convert_to_dict()

    def __convert_to_dict(self):
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

    def __init_threads(self):
        for i in range(self.__config["max_pages"]):
            if not self.__jobs.qsize() > 0:
                break
            self.__threads.append(Thread(target=self.__get_products, daemon=True))
            self.__threads[i].start()

    def __wait_for_threads(self):
        for thread in self.__threads:
            thread.join()