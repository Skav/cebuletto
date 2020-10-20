from assets.databases.models.BasicModel import BasicModel
from assets.databases.fields.DatabaseFields import *
from assets.CustomErrors import SerializerError

class ShopsModel(BasicModel):
    idShop = IntegerField(primary=True, max_length=11, not_null=True)
    shopName = VarcharField(max_length=45, not_null=True)
    searchCounter = IntegerField(max_length=10, unsigned=True, default=0)

    def __init__(self):
        super().__init__('shops')

    def create_row(self, name: str):
        query = "INSERT INTO shops VALUES(default, %s, default)"
        self._cursor.execute(query, (name,))
        self._db.commit()

    def delete_row_by_name(self, name: str):
        query = "DELETE FROM shops WHERE shopName = %s"
        self._cursor.execute(query, (name,))
        self._db.commit()