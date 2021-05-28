from assets.database.models.BasicModel import BasicModel
from assets.database.fields.DatabaseFields import IntegerField, VarcharField


class ShopsModel(BasicModel):
    idShop = IntegerField(primary=True, max_length=11, not_null=True)
    name = VarcharField(max_length=45, not_null=True)
    searchCounter = IntegerField(max_length=10, unsigned=True, default=0)

    def __init__(self):
        super().__init__('shops')

    def create_row(self, name: str):
        query = "INSERT INTO shops VALUES(default, %s, default)"
        self._cursor.execute(query, (name,))
        self._db.commit()

    def get_row_by_name(self, name: str):
        query = "SELECT * FROM shops WHERE name = %s"
        self._cursor.execute(query, (name,))
        return self._cursor.fetchone()

    def get_counter_value_by_name(self, name: str):
        query = "SELECT searchCounter FROM shops WHERE name = %s"
        self._cursor.execute(query, (name,))
        return self._cursor.fetchone()

    def delete_row_by_name(self, name: str):
        query = "DELETE FROM shops WHERE name = %s"
        self._cursor.execute(query, (name,))
        self._db.commit()

    def update_row_by_id(self, id_shop: int, name: str, search_counter: int):
        query = "UPDATE shops SET name = %s, searchCounter = %s WHERE idShop = %s"
        self._cursor.execute(query, (name, search_counter, id_shop))
        self._db.commit()

    def update_name_by_id(self, id_shop: int, name: str):
        query = "UPDATE shops SET name = %s WHERE idShop = %s"
        self._cursor.execute(query, (name, id_shop))
        self._db.commit()

    def update_counter_by_id(self, id_shop: int, value: int):
        query = "UPDATE shops set searchCounter = %s WHERE idShop = %s"
        self._cursor.execute(query, (value, id_shop))
        self._db.commit()
