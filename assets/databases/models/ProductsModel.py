from assets.databases.models.BasicModel import BasicModel
from assets.databases.fields.DatabaseFields import *

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