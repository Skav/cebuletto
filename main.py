import json
from datetime import datetime
from webScrapper import webScrapper

'''
TODO:
Clean code (!)
Add rest api (?)
Add some gui (web page)
Add option to choose on what pages we want search (in gui/rest api version) 50% done
Add more shops
'''

def main():
    print("Produkty oddzielaj ';' jezeli jest ich wiecej niz 1")
    product_name = input("Podaj interesujacy cie produkt(y): ")
    product_name = product_name.split(';')

    start = datetime.now()
    scrapper = webScrapper(product_name)
    shop_list = scrapper.get_shops_list()
    products_list = scrapper.find_products(shop_list)
    # with open('data.json', ) as f:
    #     file = json.load(f)
    results = scrapper.sort_products_by_price(products_list)
    print('execution time: ', datetime.now()-start)

    print(results)

main()