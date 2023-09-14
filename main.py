from assets.database.models.TagsToProductsModel import *
from assets.database.models.ProductsModel import ProductsModel
from assets.database.models.ProductsTagsModel import ProductsTagsModel
from assets.database.Interfaces.TagsToProductsInterface import TagsToProductsInterface
from assets.CustomErrors import SerializerError
from dotenv import load_dotenv
from assets.database.Interfaces.ShopsInterface import ShopsInterface
from assets.database.Interfaces.ProductsInterface import ProductsInterface
from assets.database.Interfaces.ProductsTagsInterface import ProductsTagsInterface
from decimal import Decimal
from assets.serializers.ModelsSerializers import ModelSerializer

load_dotenv()


def main():
    # print()
    # data = {
    #     "name": "Adbl Vampire Light",
    #     "shopName": "mrcleaner",
    #     "price": Decimal(20.00),
    #     "discountPrice": Decimal(39.00),
    #     "productUrl": "sklep.pl/url",
    #     "imageUrl": "sklep.pl/zdj",
    #     "available": 1,
    # }
    # product_model = ProductsModel()
    # product_interface = ProductsInterface()
    # shop_interface = ShopsInterface()
    # serializer = ModelSerializer(product_model, data)
    #
    # print(serializer.is_valid)
    # print(serializer.errors)

    shops = ["shop1", "shop2", "shop3", "shop4"]
    products = [1,2,3,4,5]
    products2 = [2,1]

    print({k: [v for v in products if v not in products2] for k in shops})

main()
