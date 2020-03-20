import pandas
from bs4 import BeautifulSoup
from selenium import webdriver
import json

product_dict = {}
with open('shops.json') as f:
    data = json.load(f)

product = 'fluffy dryer'#input("Podaj interesujacy cie produkt: ").replace(' ', '+')
url = 'https://mrcleaner.pl/s?q={}'.format(product)
driver = webdriver.PhantomJS('/home/skav/Pobrane/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
driver.set_window_size(1120, 550)
driver.get(url)
soup = BeautifulSoup(driver.page_source, 'html.parser')

for key in data.keys():
    shop = data[key]

    products_list = soup.find(shop["all_products_container"]["type"], attrs=shop["all_products_container"]["attrs"])
    products = products_list.find_all_next(shop["products_container"]["type"], attrs=shop["products_container"]["attrs"])

    for product in products:
        if "product_price_container" in shop.keys():
            price_div = product.find(shop["product_price_container"]["type"], attrs=shop["product_price_container"]["attrs"])
            regular_price = price_div.find(shop["product_price"]["type"], attrs=shop["product_price"]["attrs"]).text

            if "product_discount_price" in shop.keys():
                discount_price = price_div.find(shop["product_discount_price"]["type"], attrs=shop["product_discount_price"]["attrs"]).text
        else:
            regular_price = product.find(shop["product_price"]["type"], attrs=shop["product_price"]["attrs"]).text

            if "product_discount_price" in shop.keys():
                discount_price = product.find(shop["product_discount_price"]["type"], attrs=shop["product_discount_price"]["attrs"]).text

        name_container = product.find(shop["product_name"]["type"], attrs=shop["product_name"]["attrs"])
        if not name_container.text:
            name = name_container['title']
        else:
            name = name_container.text

        link = product.find(shop["product_url"]["type"], attrs=shop["product_url"]["attrs"])['href']

        product_dict[name] = {'price': regular_price, 'discount_price': discount_price, 'link': link}

print(product_dict)
