from typing import Any, Self


class Singleton:
    _instance = None
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:  # noqa: ARG003
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self: Self, x: int) -> None:
        if not hasattr(self, "x"):
            self.x = x


sg1 = Singleton(10)
sg2 = Singleton(20)

print(sg1.x, sg2.x) # 10 10
print(sg1 is sg2) # True




