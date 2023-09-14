from assets.database.models.ShopsModel import ShopsModel
from assets.serializers.ModelsSerializers import ModelSerializer
from assets.CustomErrors import SerializerError


class ShopsInterface:
    @staticmethod
    def check_shop_exist_by_name(name: str):
        serializer = ModelSerializer(ShopsModel, {"name": name}, ["name"])

        if serializer.is_valid:
            shop_data = ShopsModel().get_row_by_name(serializer.data["name"])
            return shop_data["idShop"] if shop_data else False
        else:
            raise SerializerError(serializer.errors)

    @staticmethod
    def get_all_shops():
        return ShopsModel().get_all()

    @staticmethod
    def get_shop_by_id(shop_id: int):
        serializer = ModelSerializer(ShopsModel, {"idShop": shop_id}, ["idShop"])

        if serializer.is_valid:
            return ShopsModel().get_row_by_id(serializer.data["idShop"])
        else:
            raise SerializerError(serializer.errors)
