from assets.database.models.TagsToProductsModel import *
from assets.serializers.ModelsSerializers import ShopsSerializer
from assets.CustomErrors import SerializerError
from dotenv import load_dotenv

load_dotenv()

def main():
    # serializer = ShopsSerializer({"shopName": True})
    db = TagsToProductsModel()
    print(db.get_row_with_relations_names_by_id(1))
    # serializer = ShopsSerializer({"shopName": "noelo"})
    # if serializer.is_valid:
    #     db.create_row(serializer.data['shopName'])
    # else:
    #     raise SerializerError(serializer.errors)pip

main()