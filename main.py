from assets.databases.models.ShopsModel import ShopsModel
from assets.serializers.ModelsSerializers import ShopsSerializer
from assets.CustomErrors import SerializerError
from dotenv import load_dotenv

load_dotenv()

def main():
    # serializer = ShopsSerializer({"shopName": True})
    db = ShopsModel()
    print(db.get_row_by_name("mrcleaner"))
    # serializer = ShopsSerializer({"shopName": "noelo"})
    # if serializer.is_valid:
    #     db.create_row(serializer.data['shopName'])
    # else:
    #     raise SerializerError(serializer.errors)pip

main()