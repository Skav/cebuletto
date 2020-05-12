from threading import Thread
from bs4 import BeautifulSoup
from selenium import webdriver
from re import sub
from decimal import Decimal
from assets.CustomErrors import WebDriverNotFound


class ScrapperThread(Thread):

    def __init__(self, error_container, jobs, results, config, shops_info):
        Thread.__init__(self)
        self.__error = error_container
        self.__results = results
        self.__jobs = jobs
        self.__config = config
        self.__shops_info = shops_info

    def run(self):
        try:
            while not self.__jobs.empty():
                data = self.__jobs.get()
                shop_products = {data.product: {}}

                print(data.shop, " ", data.product)

                driver = self.__set_web_driver()
                page = self.__get_page(data.url, driver)
                products = self.__get_products_list(page["source"], data.shop_struct)

                if not products:
                    results = self.__try_find_data_on_product_page(page, data)
                    if not results:
                        self.__no_product_in_shop(shop_products, data.product, data.shop)
                        continue
                    shop_products[data.product][data.shop] = results
                    self.__done_task(shop_products)
                    continue

                list_of_products = self.__get_products_data(products, data.product_name_keys, data.shop_struct,
                                                            data.shop)

                if not list_of_products:
                    list_of_products = self.__try_find_data_on_product_page(page, data)
                    if not list_of_products:
                        self.__no_product_in_shop(shop_products, data.product, data.shop)
                        continue

                shop_products[data.product][data.shop] = list_of_products
                self.__done_task(shop_products)
        except Exception as e:
            self.__error.put(e)

    def __try_find_data_on_product_page(self, page, data):
        if not data.shop_info["redirect_to_product_page"]:
            return False
        single_product_struct = data.shop_struct["single_product_page"]

        return self.__get_products_data(page['source'], data.product_name_keys, single_product_struct,
                                        data.shop, page['url'])

    def __done_task(self, data):
        self.__results.put(data)
        self.__jobs.task_done()

    def __get_products_data(self, products, product_name_keys, shop_struct, shop, url=None):
        list_of_products = {}
        for product in products:
            name = self.__get_name(product, product_name_keys, shop_struct)
            if not name:
                continue

            link = self.__get_link(product, shop_struct, shop) if not url else url
            price = self.__get_price(product, shop_struct)
            image_url = self.__get_image_url(product, shop_struct, shop)
            available = False if not price else self.__is_product_available(product, shop_struct)

            if not price:
                price = {"regular": "0", "discount": "0"}

            list_of_products[name] = {'price': price["regular"], 'discount_price': price["discount"],
                                      'link': link, 'image_url': image_url, 'available': available}
        return list_of_products

    def __set_web_driver(self):
        if self.__config["web_browser"] == "Chrome":
            browser_options = webdriver.ChromeOptions()
            browser_options.add_argument('headless')
            return webdriver.Chrome(options=browser_options)
        elif self.__config["web_browser"] == "Firefox":
            browser_options = webdriver.FirefoxOptions()
            browser_options.add_argument('headless')
            return webdriver.Firefox(options=browser_options)
        else:
            raise WebDriverNotFound(self.__config["web_browser"])

    def __get_page(self, url, driver):
        driver.get(url)
        data = {"url": driver.current_url,
                "source": BeautifulSoup(driver.page_source, 'html.parser')}
        driver.close()
        return data

    def __get_products_list(self, soup, shop_struct):
        products_list = soup.find(shop_struct["all_products_container"]["type"],
                                  attrs=shop_struct["all_products_container"]["attrs"])
        if not products_list:
            return False

        return products_list.find_all_next(shop_struct["products_container"]["type"],
                                           attrs=shop_struct["products_container"]["attrs"])

    def __get_name(self, product, product_name_keys, shop_struct):
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

    def __get_link(self, product, shop_struct, key):
        if "child_type" in shop_struct["product_url"]:
            link_container = product.find(shop_struct["product_url"]["type"],
                                          attrs=shop_struct["product_url"]["attrs"])
            return link_container.find(shop_struct["product_url"]["child_type"],
                                       attrs=shop_struct["product_url"]["child_attrs"])['href']
        link = product.find(shop_struct["product_url"]["type"], attrs=shop_struct["product_url"]["attrs"])['href']

        if not self.__shops_info[key]["has_domain_in_link"]:
            link = "{}{}".format(self.__shops_info[key]["url"], link)

        return link

    def __get_price(self, product, shop_struct):
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

    def __get_image_url(self, product, shop_struct, shop):
        if "product_image_container" in shop_struct.keys():
            image_container = product.find(shop_struct['product_image_container']['type'],
                                           attrs=shop_struct['product_image_container']['attrs'])

            image_url = image_container.find(shop_struct['product_image']['type'],
                                            attrs=shop_struct['product_image']['attrs'])

            if not image_url and "alt_product-image" in shop_struct.keys():
                image_url = image_container.find(shop_struct['alt_product_image']['type'],
                                                 attrs=shop_struct['alt_product_image']['attrs'])
        else:
            image_url = product.find(shop_struct['product_image']['type'],
                                            attrs=shop_struct['product_image']['attrs'])

            if not image_url and "alt_product_image" in shop_struct.keys():
                image_url = product.find(shop_struct['product_image']['type'],
                                             attrs=shop_struct['product_image']['attrs'])

        if 'url_location' in shop_struct['product_image'] and shop_struct['product_image']['url_location'] in image_url.attrs:
            image_url = image_url[shop_struct['product_image']['url_location']]
        else:
            image_url = image_url['src']

        if not self.__shops_info[shop]['has_link_in_image_url']:
            image_url = '{}{}'.format(self.__shops_info[shop]["url"], image_url)

        return image_url

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

    def __no_product_in_shop(self, shop_products, product_name, shop):
        shop_products[product_name][shop] = {product_name: "Brak"}
        self.__done_task(shop_products)

