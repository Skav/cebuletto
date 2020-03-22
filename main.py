from threading import Thread
from datetime import datetime
from queue import Queue
from bs4 import BeautifulSoup
from selenium import webdriver
import json

'''
TODO:
Add async (actually learn how to execute it in thread)
Add config file
Add list of product to search
'''
def main():
    product_name = input("Podaj interesujacy cie produkt: ")
    threads = []
    queue = Queue()
    start = datetime.now()
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument('headless')
    with open('shops_structure.json') as f:
        shops_structure = json.load(f)

    with open('shops_info.json') as f:
        shop_info = json.load(f)

    #products_list = {}
    for i, key in enumerate(shops_structure.keys()):
        threads.append(Thread(target=get_products,args=(shops_structure, shop_info, product_name, key, browser_options, queue), daemon=True))
        threads[i].start()

    for thread in threads:
        thread.join()

    print('execution time:', datetime.now()-start)
    print(queue.queue)


def get_products(shops_structure, shop_info, product_name, key, browser_options,queue):
        print(key)
        shop_struct = shops_structure[key]
        product_name_keys = product_name.lower().split(" ")
        product_separated_name = product_name.replace(" ", shop_info[key]["separator"])
        url = "{}{}".format(shop_info[key]["url"], product_separated_name)
        product_dict = {}

        driver = webdriver.Chrome(options=browser_options)
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

            product_dict[name] = {'price': price["regular"], 'discount_price': price["discount"], 'link': link}
        queue.put(product_dict)

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