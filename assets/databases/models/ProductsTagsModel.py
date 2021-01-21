from assets.databases.models.BasicModel import BasicModel
from assets.databases.fields.DatabaseFields import *

class ProductsTagsModel(BasicModel):
    idProductsTags = IntegerField(primary=True, max_length=11, not_null=True)
    productTags = VarcharField(max_length=45, not_null=True)
    searchCounter = IntegerField(max_length=11, unsigned=True, not_null=True, default=1)
    
    def __init__(self):
        super().__init__('productsTags')