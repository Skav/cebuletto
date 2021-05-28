from assets.database.models.BasicModel import BasicModel
from assets.database.fields.DatabaseFields import IntegerField, VarcharField, DecimalField, DatetimeField, BooleanField


class ProductsModel(BasicModel):
    idProduct = IntegerField(primary=True, max_length=11, not_null=True)
    idShop = IntegerField(max_length=11, not_null=True, foreign_key='shops')
    name = VarcharField(max_length=100, not_null=True)
    price = DecimalField(max_digits=6, decimal_places=2, not_null=True, default=0.00)
    discountPrice = DecimalField(max_digits=6, decimal_places=2, not_null=True, default=0.00)
    productUrl = VarcharField(max_length=200, not_null=True)
    imageUrl = VarcharField(max_length=200)
    available = BooleanField(not_null=True, default=True)
    lastUpdate = DatetimeField(auto_now_on_add=True, auto_now_on_update=True, not_null=True)

    def __init__(self):
        super().__init__('products')

    def create_row(self, id_shop: int, name: str, price: str, discount_price: str, product_url: str, image_url: str, available: bool):
        query = "INSERT INTO products VALUES (default, %s, %s, %s, %s, %s, %s, %s, default)"
        self._cursor.execute(query, (id_shop, name, price, discount_price, product_url, image_url, available))
        self._db.commit()

    def get_rows_with_shop_name(self, limit=100):
        query = """SELECT products.*, shops.name FROM products INNER JOIN shops on products.idShop = shops.idShop
                LIMIT = %s"""
        self._cursor.execute(query, (limit,))

    def get_rows_by_shop_id(self, id_shop: int, limit=100):
        query = "SELECT * FROM products WHERE idShop = %s LIMIT %s"
        self._cursor.execute(query, (id_shop, limit))
        return self._cursor.fetchall()

    def get_row_by_id_with_shop_name(self, product_id: int):
        query = """SELECT products.*, shops.name FROM products INNER JOIN shops on products.idShop = shops.idShop
                WHERE idProduct = %s"""
        self._cursor.execute(query, (product_id,))
        return self._cursor.fetchone()

    def get_row_by_name(self, product_name: str):
        query = "SELECT * FROM products WHERE name = %s"
        self._cursor.execute(query, (product_name,))
        return self._cursor.fetchone()

    def check_is_product_available(self, product_name: str):
        query = "SELECT available FROM products WHERE name = %s"
        self._cursor.execute(query, (product_name,))

    def update_product_availability_by_name(self, product_name: bool, is_available: bool):
        query = "UPDATE products SET available=%s WHERE name = %s"
        self._cursor.execute(query, (is_available, product_name))
        self._db.commit()
