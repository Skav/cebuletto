from .BasicModel import BasicModel
from .DatabaseColumns import *

class ShopsModel(BasicModel):
    idShop = PrimaryField()
    shopName = VarcharField(max_length=45, not_null=True)
    searchCounter = IntegerField(max_length=8, not_null=True)