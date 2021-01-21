from assets.databases.models.BasicModel import BasicModel
from assets.databases.fields.DatabaseFields import *

class TagsToProductsModel(BasicModel):

    idTagsToProduct = IntegerField(primary=True, max_length=11, not_null=True)
    idProducts = IntegerField(foreign_key='products', max_length=11, not_null=True)
    idProductTag = IntegerField(foreign_key='productsTags', max_length=11, not_null=True)
    lastUpdate = DatetimeField(auto_now_on_add=True, auto_now_on_update=True, not_null=True)

    def __init__(self):
        super().__init__('tagsToProducts')