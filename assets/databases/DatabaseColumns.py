from datetime import datetime


class BaseField:
    def __init__(self, field_type, max_length: int, not_null: bool, default, on_update, writeable: bool):
        self.field_type = field_type
        self.max_length = max_length
        self.not_null = not_null
        self.writeable = writeable
        self.default = default
        self.on_update = on_update


class PrimaryField(BaseField):
    def __init__(self):
        super().__init__(
            field_type=int,
            max_length=4,
            not_null=True,
            default=None,
            on_update=None,
            writeable=False
        )


class VarcharField(BaseField):
    def __init__(self, max_length: int, not_null: bool, default: str, on_update: str, writeable: bool):
        super().__init__(
            field_type=str,
            max_length=max_length or 45,
            not_null=not_null or True,
            default=default or None,
            on_update=on_update or None,
            writeable=writeable or True
        )


class IntegerField(BaseField):
    def __init__(self, max_length: int, not_null: bool, default: int, on_update: int, writeable: bool):
        super().__init__(
            field_type=int,
            max_length=max_length or 10,
            not_null=not_null or True,
            default=default or None,
            on_update=on_update or None,
            writeable=writeable or True
        )


class DecimalField(BaseField):
    def __init__(self, max_length: int, precision: int, not_null: bool, default: float, on_update: float, writeable: bool):
        self.precision = precision or 2
        super().__init__(
            field_type=float,
            max_length=max_length or 5,
            not_null=not_null or True,
            default=default or None,
            on_update=on_update or None,
            writeable=writeable or True
        )


class BooleanField(BaseField):
    def __init__(self, not_null: bool, default: bool, on_update: bool, writeable: bool):
        super().__init__(
            field_type=bool,
            max_length=1,
            not_null=not_null or True,
            default=default or None,
            on_update=on_update or None,
            writeable=writeable or True
        )


class TimestampField(BaseField):
    def __init__(self, not_null: bool, set_auto_now: bool, set_now_on_update: bool, default: datetime,
                 on_update: datetime, writeable: bool):
        self.set_auto_now = set_auto_now or False
        self.set_now_on_update = set_now_on_update or False
        super().__init__(
            field_type=datetime,
            max_length=26,
            not_null=not_null or True,
            default=default or None,
            on_update=on_update or None,
            writeable=writeable or True
        )


class ForeignKey(BaseField):
    def __init__(self, table: str, name: str, on_delete: str, not_null: bool, default: str, on_update: str, writeable: bool):
        self.table = table
        self.name = name
        self.on_delete = on_delete or "NO ACTION"
        super().__init__(
            field_type=int,
            max_length=4,
            not_null=not_null or False,
            default=default or None,
            on_update=on_update or "NO ACTION",
            writeable=writeable or True
        )
