from assets.databases.models.BasicModel import BasicModel
from assets.databases.fields.DatabaseFields import *

class HistoryOfPricesModel(BasicModel):
    idHistoryOfPrice = IntegerField(primary=True, max_length=11, not_null=True)
    idProduct = IntegerField(foreign_key='products', max_length=11, not_null=True)
    price = DecimalField(max_digits=6, decimal_places=2, not_null=True, default=0.00)
    discountPrice = DecimalField(max_digits=6, decimal_places=2, not_null=True, default=0.00)
    priceData = DatetimeField(auto_now_on_add=True, not_null=True, writeable=False)

    def __init__(self):
        super().__init__('historyOfPrices')