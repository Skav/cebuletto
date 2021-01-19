from assets.databases.models.BasicModel import BasicModel
from assets.databases.fields.DatabaseFields import *


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

    def get_row_by_name(self, name: str):
        query = "SELECT * FROM shops WHERE shopName = %s"
        self._cursor.execute(query, (name,))
        return self._cursor.fetchone()

    def get_counter_value_by_name(self, name: str):
        query = "SELECT searchCounter FROM shops WHERE shopName = %s"
        self._cursor.execute(query, (name,))
        return self._cursor.fetchone()

    def delete_row_by_name(self, name: str):
        query = "DELETE FROM shops WHERE shopName = %s"
        self._cursor.execute(query, (name,))
        self._db.commit()

    def update_row_by_id(self, shop_id: int, name: str, search_counter: int):
        query = "UPDATE shops SET shopName = %s, searchCounter = %s WHERE idShop = %s"
        self._cursor.execute(query, (name, search_counter, shop_id))
        self._db.commit()

    def update_name_by_id(self, shop_id: int, name: str):
        query = "UPDATE shops SET shopName = %s WHERE idShop = %s"
        self._cursor.execute(query, (name, shop_id))
        self._db.commit()

    def update_counter_by_id(self, shop_id: int, value: int):
        query = "UPDATE shops set searchCounter = %s WHERE idShop = %s"
        self._cursor.execute(query, (value, shop_id))
        self._db.commit()