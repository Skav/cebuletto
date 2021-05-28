from assets.database.models.BasicModel import BasicModel
from assets.database.fields.DatabaseFields import IntegerField, DecimalField, DatetimeField


class HistoryOfPricesModel(BasicModel):
    idHistoryOfPrice = IntegerField(primary=True, max_length=11, not_null=True)
    idProduct = IntegerField(foreign_key='products', max_length=11, not_null=True)
    price = DecimalField(max_digits=6, decimal_places=2, not_null=True, default=0.00)
    discountPrice = DecimalField(max_digits=6, decimal_places=2, not_null=True, default=0.00)
    priceData = DatetimeField(auto_now_on_add=True, not_null=True, writeable=False)

    def __init__(self):
        super().__init__('historyOfPrices')

    def get_row_with_product_name_by_product_id(self, id_product: int):
        query = """SELECT historyOfPrices.idHistoryOfPrices, product.name, historyOfPrices.price, 
                historyOfPrices.discountPrice, historyOfPrices.priceData FROM historyOfPrices
                INNER JOIN products ON historyOfPrices.idProduct = products.idProduct
                WHERE historyOfPrices.idProduct = %s LIMIT 1"""
        self._cursor.execute(query, (id_product,))
        return self._cursor.fetchone()

    def get_row_by_product_name(self, product_name: str):
        query = """SELECT historyOfPrices.* FROM historyOfPrices
                INNER JOIN product ON historyOfPrices.idProduct = products.idProduct
                WHERE product.name = %s LIMIT 1"""
        self._cursor.execute(query, (product_name,))
        return self._cursor.fetchone()

    def add_row(self, id_product: int, price: int, discount_price: int):
        query = "INSERT INTO historyOfPrices VALUES (default, %s, %s, %s, default)"
        self._cursor.execute(query, (id_product, price, discount_price))
        self._db.commit()
