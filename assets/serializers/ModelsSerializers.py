from ..database.fields.DatabaseFields import *
from ..database.fields.FieldsValues import NOT_PROVIDED
from assets.database.models.ShopsModel import ShopsModel
from .BaseSerializer import BaseSerializer


class ModelSerializer(BaseSerializer):
    def __init__(self, model, data: dict):
        super().__init__()
        self._model = model
        self._input_data = data
        self._table_fields = [x for x in dir(model) if not callable(getattr(model, x)) and not x.startswith("__")
                              and not x.startswith("_")]
        self.data = None
        self.__serialize_data()

    def __serialize_data(self):
        if not self.__are_not_null_fields_correct():
            return False

        for key, value in self._input_data.items():
            db_field = getattr(self._model, key)

            if len(value) > db_field.max_length:
                self._set_error(f"{key} is too long")
            if type(value) != db_field.field_type:
                self._set_error(f"{key} have incorrect data type")

            if self.errors:
                return False

        self.data = self._input_data
        return True

    def __are_not_null_fields_correct(self):
        not_null_fields = [x for x in self._table_fields if getattr(self._model, x).not_null
                           and getattr(self._model, x).primary is False]
        missing_fields = [x for x in self._table_fields if x not in self._input_data.keys()
                          and x in not_null_fields
                          and getattr(self._model, x).default == NOT_PROVIDED
                          and getattr(self._model, x).writeable is False]

        empty_values = [k for k, v in self._input_data.items() if v is None or '']
        empty_not_null_fields = [x for x in empty_values if x in not_null_fields]

        if empty_not_null_fields:
            self._set_error(f"This fields required values: {empty_not_null_fields}")

        if missing_fields:
            self._set_error(f"Missing fields {missing_fields}")

        return self.is_valid


class ShopsSerializer(ModelSerializer):
    def __init__(self, data):
        model = ShopsModel()
        super().__init__(model, data)
