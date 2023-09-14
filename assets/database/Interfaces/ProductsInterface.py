from assets.database.models.ProductsModel import ProductsModel
from assets.serializers.ModelsSerializers import ModelSerializer
from assets.CustomErrors import SerializerError


class ProductsInterface:

    @staticmethod
    def add_new_product(data: dict):
        serializer = ModelSerializer(ProductsModel, data)

        if serializer.is_valid:
            ProductsModel().create_row(serializer.data["idShop"], serializer.data["name"], serializer.data["price"],
                                       serializer.data["discountPrice"], serializer.data["productUrl"],
                                       serializer.data["imageUrl"], serializer.data["available"])
            return True
        else:
            raise SerializerError(serializer.errors)

    @staticmethod
    def check_product_exist_by_name(name: str):
        serializer = ModelSerializer(ProductsModel, {"name": name}, ["name"])

        if serializer.is_valid:
            product = ProductsModel().get_row_by_name(serializer.data['name'])
            return product["idProduct"] if product else False
        else:
            raise SerializerError(serializer.errors)

    @staticmethod
    def update_existing_product_by_id(product_id: int, data: dict):
        serializer = ModelSerializer(ProductsModel, data)

        if serializer.is_valid:
            ProductsModel().update_product_data_by_id(product_id, serializer.data["name"], serializer.data['price'],
                                                      serializer.data['discountPrice'], serializer.data['productUrl'],
                                                      serializer.data['imageUrl'], serializer.data['available'])
            return True
        else:
            raise SerializerError(serializer.errors)
