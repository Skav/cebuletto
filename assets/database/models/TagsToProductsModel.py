from assets.database.models.BasicModel import BasicModel
from assets.database.fields.DatabaseFields import IntegerField, DatetimeField


class TagsToProductsModel(BasicModel):

    idTagToProduct = IntegerField(primary=True, max_length=11, not_null=True)
    idProduct = IntegerField(foreign_key='products', max_length=11, not_null=True)
    idProductTag = IntegerField(foreign_key='productsTags', max_length=11, not_null=True)
    lastUpdate = DatetimeField(auto_now_on_add=True, auto_now_on_update=True, not_null=True)

    def __init__(self):
        super().__init__('tagsToProducts')

    def get_row_with_relations_names_by_id(self, id_tags_to_products: int):
        query = """SELECT tagsToProducts.idTagsToProduct, products.name, productsTags.tag, tagsToProducts.lastUpdate
                FROM tagsToProducts
                INNER JOIN products ON tagsToProducts.idProduct = products.idProduct
                INNER JOIN productsTags ON tagsToProducts.idProductTag = productsTags.idProductTag
                WHERE tagsToProducts.idTagsToProduct = %s LIMIT 1"""
        self._cursor.execute(query, (id_tags_to_products,))
        return self._cursor.fetchone()

    def get_products_names_by_tag_id(self, id_product_tag: int, limit=100):
        query = """SELECT product.name FROM tagsToProducts
                INNER JOIN product ON product.idProduct = tagsToProduct.idProduct
                WHERE tagsToProduct.idProductTag LIMIT %s"""
        self._cursor.execute(query, (id_product_tag, limit))
        return self._cursor.fetchall()

    def get_tags_by_product_id(self, id_product: int, limit=100):
        query = """SELECT productsTags.tag FROM tagsToProducts
                INNER JOIN productsTags ON productsTags.idProductTag = tagsToProducts.idProductTag
                WHERE tagsToProducts.idProduct = %s LIMIT %s"""
        self._cursor.execute(query, (id_product, limit))
        return self._cursor.fetchall()

    def get_tags_by_product_name(self, product_name: str, limit=100):
        query = """SELECT productsTags.tag FROM tagsToProducts
                INNER JOIN product ON tagsToProducts.idProduct = products.idProduct
                INNER JOIN productsTags ON tagsToProducts.idProductTag = productsTags.idProductTag
                WHERE product.name = % LIMIT %s"""
        self._cursor.execute(query, (product_name, limit))
        return self._cursor.fetchall()

    def get_products_by_tag(self, tag: str, limit=100):
        query = """SELECT products.* FROM tagsToProducts
                INNER JOIN products ON tagsToProducts.idProduct = products.idProduct
                INNER JOIN productsTags ON tagsToProducts.idProductTag = productsTags.idProductTag
                WHERE productsTags.tag = %s LIMIT %s"""
        self._cursor.execute(query, (tag, limit))
        return self._cursor.fetchall()

    def get_products_by_tag_and_shop_id(self, tag: str, shop_id: int, limit=100):
        query = """SELECT products.* FROM tagsToProducts
                INNER JOIN products ON tagsToProducts.idProduct = products.idProduct
                INNER JOIN productsTags ON tagsToProducts.idProductTag = productsTags.idProductTag
                WHERE productsTags.tag = %s AND 
                WHERE products.idProduct = %s
                LIMIT %s"""
        self._cursor.execute(query, (tag, shop_id, limit))
        return self._cursor.fetchall()

    def create_row(self, id_product: int, id_product_tag: int):
        query = "INSERT INTO tagsToProducts VALUES (default, %s, %s, default)"
        self._cursor.execute(query, (id_product, id_product_tag))
        self._db.commit()
