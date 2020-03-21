from bs4 import BeautifulSoup
from selenium import webdriver
import json

shops_products = {}
with open('shops_structure.json') as f:
    shops_structure = json.load(f)

with open('shops_info.json') as f:
    shop_info = json.load(f)


product_name = input("Podaj interesujacy cie produkt: ")
product_name_keys = product_name.lower().split(" ")
url = 'https://mrcleaner.pl/s?q={}'.format(product_name)
driver = webdriver.PhantomJS('/home/skav/Pobrane/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
driver.set_window_size(1120, 550)

for key in shops_structure.keys():
    product_dict = {}
    shop_struct = shops_structure[key]
    product_separated_name = product_name.replace(" ", shop_info[key]["separator"])
    url = "{}{}".format(shop_info[key]["url"], product_separated_name)

    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    products_list = soup.find(shop_struct["all_products_container"]["type"], attrs=shop_struct["all_products_container"]["attrs"])

    if not products_list:
        break

    products = products_list.find_all_next(shop_struct["products_container"]["type"], attrs=shop_struct["products_container"]["attrs"])

    for product in products:
        if "product_price_container" in shop_struct.keys():
            price_div = product.find(shop_struct["product_price_container"]["type"], attrs=shop_struct["product_price_container"]["attrs"])
            regular_price = price_div.find(shop_struct["product_price"]["type"], attrs=shop_struct["product_price"]["attrs"]).text

            if "product_discount_price" in shop_struct.keys():
                discount_price = price_div.find(shop_struct["product_discount_price"]["type"], attrs=shop_struct["product_discount_price"]["attrs"]).text
        else:
            regular_price = product.find(shop_struct["product_price"]["type"], attrs=shop_struct["product_price"]["attrs"]).text

            if "product_discount_price" in shop_struct.keys():
                discount_price = product.find(shop_struct["product_discount_price"]["type"], attrs=shop_struct["product_discount_price"]["attrs"]).text


        name_container = product.find(shop_struct["product_name"]["type"], attrs=shop_struct["product_name"]["attrs"])

        if "children_type" in shop_struct["product_name"].keys():
            name_container = name_container.find(shop_struct["product_name"]["children_type"], attrs=shop_struct["product_name"]["children_attrs"])

        if not name_container.text:
            name = name_container['title']
        else:
            name = name_container.text

        if "children_type" in shop_struct["product_url"]:
            link_container = product.find(shop_struct["product_url"]["type"], attrs=shop_struct["product_url"]["attrs"])
            link = link_container.find(shop_struct["product_url"]["children_type"], attrs=shop_struct["product_url"]["children_attrs"])['href']
        else:
            link = product.find(shop_struct["product_url"]["type"], attrs=shop_struct["product_url"]["attrs"])['href']

        if all(x in name.lower() for x in product_name_keys):
            product_dict[name] = {'price': regular_price, 'discount_price': discount_price, 'link': link}

    shops_products[key] = product_dict
print(shops_products)
