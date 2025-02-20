from datetime import UTC, datetime
from typing import Any


class DatetimeMetaclass(type):
    def __init__(cls, name: str, bases: tuple, dct: dict[str, Any]) -> None:
        cls.created_at = datetime.now(UTC)
        super().__init__(name, bases, dct)


class A(metaclass=DatetimeMetaclass):
    ...


a = A()

print(a.created_at)