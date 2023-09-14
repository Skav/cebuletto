from assets.database.models.ProductsTagsModel import ProductsTagsModel
from assets.serializers.ModelsSerializers import ModelSerializer
from assets.CustomErrors import SerializerError


class ProductsTagsInterface:

    @staticmethod
    def add_product_tag(tag: str):
        serializer = ModelSerializer(ProductsTagsModel, {"tag": tag})

        if serializer.is_valid:
            ProductsTagsModel().create_row(serializer.data["tag"])
            return True
        else:
            raise SerializerError(serializer.errors)

    @staticmethod
    def check_tag_exist(tag: str):
        serializer = ModelSerializer(ProductsTagsModel, {"tag": tag})

        if serializer.is_valid:
            return True if ProductsTagsModel().get_row_by_tag(serializer.data["tag"]) else False
        else:
            raise SerializerError(serializer.errors)

    @staticmethod
    def update_tag_counter(tag: str):
        serializer = ModelSerializer(ProductsTagsModel, {"tag": tag})

        if serializer.is_valid:
            products_tags_model = ProductsTagsModel()
            tag = products_tags_model.get_row_by_tag(serializer.data["tag"])
            if tag:
                products_tags_model.update_search_counter_by_id(tag['idProductTag'], tag['searchCounter'])
                return True
            else:
                return False
        else:
            raise SerializerError(serializer.errors)
