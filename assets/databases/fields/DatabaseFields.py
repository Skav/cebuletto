from datetime import datetime
from decimal import Decimal
from .FieldsTypes import NOT_PROVIDED

class BaseField:
    def __init__(self, field_type=None, max_length=None, not_null=False, default=NOT_PROVIDED,
                 on_update=NOT_PROVIDED, writeable=True, unique=False, primary=False):
        self.field_type = field_type
        self.max_length = max_length
        self.not_null = not_null
        self.writeable = writeable
        self.default = default
        self.on_update = on_update
        self.unique = unique
        self.primary = primary


class VarcharField(BaseField):
    def __init__(self, **kwargs):
        kwargs["field_type"] = str
        super().__init__(**kwargs)


class IntegerField(BaseField):
    def __init__(self, unsigned=False, **kwargs):
        self.unsigned = unsigned
        kwargs["field_type"] = int

        super().__init__(**kwargs)


class DecimalField(BaseField):
    def __init__(self, max_digits=None, decimal_places=None, **kwargs):
        self.decimal_places = decimal_places
        kwargs["max_length"] = max_digits
        kwargs["field_type"] = Decimal

        super().__init__(**kwargs)


class BooleanField(BaseField):
    def __init__(self, **kwargs):
        kwargs["field_type"] = int
        kwargs["max_length"] = 1

        super().__init__(**kwargs)

    def convert_bool_to_int(self, boolean):
        return int(boolean)


class DatetimeField(BaseField):
    def __init__(self, auto_now_on_add=False, auto_now_on_update=False, **kwargs):
        self.auto_now_on_add = auto_now_on_add
        self.auto_now_on_update = auto_now_on_update
        kwargs["field_type"] = datetime

        if self.auto_now_on_update or self.auto_now_on_add:
            kwargs['writeable'] = False

        super().__init__(**kwargs)
