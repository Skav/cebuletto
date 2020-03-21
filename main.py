from bs4 import BeautifulSoup
from selenium import webdriver
import json


def main():
    with open('shops_structure.json') as f:
        shops_structure = json.load(f)

    with open('shops_info.json') as f:
        shop_info = json.load(f)


    product_name = input("Podaj interesujacy cie produkt: ")
    driver = webdriver.PhantomJS('/home/skav/Pobrane/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
    driver.set_window_size(1120, 550)
    products_list = get_products(shops_structure, shop_info, product_name, driver)
    print(products_list)


def get_products(shops_structure, shop_info, product_name, driver):
    shops_products={}
    for key in shops_structure.keys():
        product_dict = {}
        shop_struct = shops_structure[key]
        product_name_keys = product_name.lower().split(" ")
        product_separated_name = product_name.replace(" ", shop_info[key]["separator"])
        url = "{}{}".format(shop_info[key]["url"], product_separated_name)

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        products_list = soup.find(shop_struct["all_products_container"]["type"], attrs=shop_struct["all_products_container"]["attrs"])

        if not products_list:
            continue

        products = products_list.find_all_next(shop_struct["products_container"]["type"], attrs=shop_struct["products_container"]["attrs"])

        for product in products:
            name = get_name(product, product_name_keys, shop_struct)
            if not name:
                continue

            price = get_price(product, shop_struct)
            link = get_link(product, shop_struct)

            product_dict[name] = {'price': price["price"], 'discount_price': price["discount_price"], 'link': link}
        shops_products[key] = product_dict
    return shops_products

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

    return {"price": regular_price, "discount_price": discount_price}


def get_link(product, shop_struct):
    if "children_type" in shop_struct["product_url"]:
        link_container = product.find(shop_struct["product_url"]["type"], attrs=shop_struct["product_url"]["attrs"])
        return link_container.find(shop_struct["product_url"]["children_type"],
                                   attrs=shop_struct["product_url"]["children_attrs"])['href']
    return product.find(shop_struct["product_url"]["type"], attrs=shop_struct["product_url"]["attrs"])['href']

main()