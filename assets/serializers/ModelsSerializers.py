from ..databases.fields.DatabaseFields import *
from ..databases.fields.FieldsTypes import NOT_PROVIDED
from assets.databases.models.ShopsModel import ShopsModel


class ModelSerializer:
    def __init__(self, model, data: dict):
        self.is_valid = True
        self.errors = ''
        self._model = model
        self._input_data = data
        self._table_fields = [x for x in dir(model) if not callable(getattr(model, x)) and not x.startswith("__")
                              and not x.startswith("_")]
        self.data = None
        self.serialize()

    def serialize(self):
        self.__check_not_null_fields()

        if self.errors:
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

    def __check_not_null_fields(self):
        not_null_fields = [x for x in self._table_fields if getattr(self._model, x).not_null]
        empty_values = [k for k, v in self._input_data.items() if v is None or '']
        missing_fields = [x for x in self._table_fields if x not in self._input_data.keys()
                          and getattr(self._model, x).not_null is True
                          and getattr(self._model, x).default == NOT_PROVIDED
                          and getattr(self._model, x).primary is False]

        empty_not_null_fields = [x for x in empty_values if x in not_null_fields]

        if empty_not_null_fields:
            self._set_error(f"This fields reqired values: {empty_not_null_fields}")

        if missing_fields:
            self._set_error(f"Missing fields {missing_fields}")

    def _set_error(self, message):
        if self.is_valid is True:
            self.is_valid = False
        self.errors = f"{self.errors}; {message}" or message


class ShopsSerializer(ModelSerializer):
    def __init__(self, data):
        model = ShopsModel()
        super().__init__(model, data)
