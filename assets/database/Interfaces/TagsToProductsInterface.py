from assets.database.models.TagsToProductsModel import TagsToProductsModel
from assets.database.models.ProductsTagsModel import ProductsTagsModel
from assets.database.models.ProductsModel import ProductsModel
from assets.serializers.ModelsSerializers import ModelSerializer
from assets.CustomErrors import SerializerError


class TagsToProductsInterface:

    @staticmethod
    def get_products_by_tag_and_shop_id(tag: str, shop_id: int, limit=100):

        if type(limit) is not int:
            raise SerializerError("Limit needs to be a integer!")

        tag_serializer = ModelSerializer(ProductsTagsModel, {"tag": tag})
        shop_serializer = ModelSerializer(ProductsModel, {"idShop": shop_id}, ["idShop"])

        if tag_serializer.is_valid and shop_serializer.is_valid:
            return TagsToProductsModel().get_products_by_tag_and_shop_id(tag_serializer.data['tag'],
                                                                         shop_serializer.data["idShop"])
        else:
            raise SerializerError(f"{tag_serializer.errors} {shop_serializer.errors}")

    @staticmethod
    def add_product_to_tag(tag: str, product_name: str):
        products_tag_model = ProductsTagsModel()
        product_model = ProductsModel()
        tag_serializer = ModelSerializer(products_tag_model, {"tag": tag})
        product_serializer = ModelSerializer(product_model, {"name": product_name}, ['name'])

        if tag_serializer.is_valid and product_serializer.is_valid:
            product_id = product_model.get_row_by_name(product_serializer.data["name"])['idProduct']
            tag_id = products_tag_model.get_row_by_tag(tag_serializer.data['tag'])['idProductTag']

            TagsToProductsModel().create_row(product_id, tag_id)
            return True
        else:
            raise SerializerError(f"{product_serializer.errors} {tag_serializer.errors}")
