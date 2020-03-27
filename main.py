from datetime import datetime
from webScrapper import webScrapper

'''
TODO:
(?) Add async (actually learn how to execute it in thread)
Clean code (!)
Add rest api (?)
Add some gui (web page)
Add option to choose on what pages we want search (in gui/rest api version)
'''

def main():
    print("Produkty oddzielaj ';' jezeli jest ich wiecej niz 1")
    product_name = input("Podaj interesujacy cie produkt(y): ")
    product_name = product_name.split(';')

    start = datetime.now()
    scrapper = webScrapper(product_name)
    products_list = scrapper.find_products()
    print('execution time: ', datetime.now()-start)

    print(products_list)

main()