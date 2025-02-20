from typing import Any, Self


class Singleton(type):
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if not hasattr(cls, "_instance"):
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class A(metaclass=Singleton):
    def __init__(self: Self, x: int) -> None:
        self.x = x


a1 = A(10)
a2 = A(20)

print(a1.x, a2.x) # 10 10
print(a1 is a2) # True
