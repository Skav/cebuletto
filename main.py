from threading import Thread
from datetime import datetime
from queue import Queue
from bs4 import BeautifulSoup
from selenium import webdriver
import json

'''
TODO:
(?) Add async (actually learn how to execute it in thread)
Add list of product to search
Clean code (!)
Add rest api (?)
Add some gui (web page)
Add option to choose on what pages we want search
Make results more readable (50%)
'''
def main():
    product_name = input("Podaj interesujacy cie produkt: ")
    threads = []
    results = Queue()
    jobs = Queue()
    products_list = {}
    start = datetime.now()

    with open('config.json') as f:
        config = json.load(f)

    with open('shops_structure.json') as f:
        shops_structure = json.load(f)

    with open('shops_info.json') as f:
        shop_info = json.load(f)

    if config["web_browser"] == "Chrome":
        browser_options = webdriver.ChromeOptions()
    elif config["web_browser"] == "Firefox":
        browser_options = webdriver.FirefoxOptions()
    else:
        return False

    browser_options.add_argument('headless')

    for key in shops_structure.keys():
        jobs.put(key)

    for i in range(config["max_pages"]):
        if not jobs.qsize() > 0:
            break

        threads.append(Thread(target=get_products, args=(shops_structure, shop_info, config, product_name, browser_options, results, jobs), daemon=True))
        threads[i].start()

    for thread in threads:
        thread.join()

    print('execution time: ', datetime.now()-start)

    print(results.queue)

    for products in results.queue:
        key = list(products.keys())[0]
        products_list[key] = products[key]
    print(products_list)



def get_products(shops_structure, shops_info, config, product_name, browser_options, result, jobs):
    while not jobs.empty():
        key = jobs.get()
        print(key)
        has_domain = shops_info[key]["has_domain_in_link"]
        shop_products = {}
        shop_struct = shops_structure[key]
        product_name_keys = product_name.lower().split(" ")
        product_separated_name = product_name.replace(" ", shops_info[key]["separator"])
        url = "{}{}".format(shops_info[key]["request_url"], product_separated_name)
        list_of_products = {}

        if config["web_browser"] == "Chrome":
            driver = webdriver.Chrome(options=browser_options)
        elif config["web_browser"] == "Firefox":
            driver = webdriver.Firefox(options=browser_options)

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        products_list = soup.find(shop_struct["all_products_container"]["type"], attrs=shop_struct["all_products_container"]["attrs"])

        if not products_list:
            return None

        products = products_list.find_all_next(shop_struct["products_container"]["type"], attrs=shop_struct["products_container"]["attrs"])

        for product in products:
            name = get_name(product, product_name_keys, shop_struct)
            if not name:
                continue

            link = get_link(product, shop_struct)
            price = get_price(product, shop_struct)

            if not has_domain:
                link = "{}{}".format(shops_info[key]["url"], link)

            list_of_products[name] = {'price': price["regular"], 'discount_price': price["discount"], 'link': link}

        shop_products[key] = list_of_products
        result.put(shop_products)
        jobs.task_done()

def get_name(product, product_name_keys, shop_struct):
    name_container = product.find(shop_struct["product_name"]["type"], attrs=shop_struct["product_name"]["attrs"])

    if "children_type" in shop_struct["product_name"].keys():
        name_container = name_container.find(shop_struct["product_name"]["children_type"],
                                             attrs=shop_struct["product_name"]["children_attrs"])

    name = name_container.text if name_container.text else name_container['title']

    if not all(x in name.lower() for x in product_name_keys):
        return False
    return name

def get_price(product, shop_struct):
    discount_price = "0"
    if "product_price_container" in shop_struct.keys():
        price_div = product.find(shop_struct["product_price_container"]["type"],
                                 attrs=shop_struct["product_price_container"]["attrs"])
        regular_price = price_div.find(shop_struct["product_price"]["type"],
                                       attrs=shop_struct["product_price"]["attrs"]).text

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

    return {"regular": regular_price, "discount": discount_price}


def get_link(product, shop_struct):
    if "children_type" in shop_struct["product_url"]:
        link_container = product.find(shop_struct["product_url"]["type"], attrs=shop_struct["product_url"]["attrs"])
        return link_container.find(shop_struct["product_url"]["children_type"],
                                   attrs=shop_struct["product_url"]["children_attrs"])['href']
    return product.find(shop_struct["product_url"]["type"], attrs=shop_struct["product_url"]["attrs"])['href']

main()