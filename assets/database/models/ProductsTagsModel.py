from assets.database.models.BasicModel import BasicModel
from assets.database.fields.DatabaseFields import *

class ProductsTagsModel(BasicModel):
    idProductTag = IntegerField(primary=True, max_length=11, not_null=True)
    tag = VarcharField(max_length=45, not_null=True)
    searchCounter = IntegerField(max_length=11, unsigned=True, not_null=True, default=1)

    def __init__(self):
        super().__init__('productsTags')

    def get_row_by_tag(self, tag: str):
        query = "SELECT * FROM productsTags WHERE tag = %s LIMIT 1"
        self._cursor.execute(query, (tag,))
        return self._cursor.fetchone()

    def create_row(self, tag: str):
        query = "INSERT INTO productsTags VALUES (default, %s, default)"
        self._cursor.execute(query, (tag,))
        self._db.commit()

    def update_row_by_id(self, id, tag, counter):
        query = "UPDATE productsTags WHERE idProductsTags = %s SET tag = %s, searchCounter = %s"
        self._cursor.execute(query, (id, tag, counter))
        self._db.commit()

    def update_search_counter_by_id(self, id: int, value: int):
        query = "UPDATE productsTags WHERE idProductsTags = %s SET searchCounter = %s"
        self._cursor.execute(query, (id, value))
        self._db.commit()

    def delete_row_by_tag(self, tag: str):
        query = "DELETE FROM tag WHERE tag = %s"
        self._cursor.execute(query, (tag,))
        self._db.commit()
