import pickle
import unittest.mock
from functools import wraps
from typing import Any, Callable, overload


@overload
def lru_cache(maxsize: int | None = None) -> Callable[..., Any]: ...
@overload
def lru_cache(maxsize: Callable[..., Any] | None = None) -> Callable[..., Any]: ...


def lru_cache(maxsize: int | None | Callable[..., Any] = None) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache = {}

        def key_creator(args: tuple[Any, ...], kwargs: dict[str, Any]) -> bytes:
            return pickle.dumps(args) + pickle.dumps(kwargs)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = key_creator(args, kwargs)
            if key in cache:
                return cache[key]
            result = func(*args, **kwargs)
            if isinstance(maxsize, int) and len(cache) >= maxsize:
                cache.pop(next(iter(cache)))
            cache[key] = result
            return result
        return wrapper

    if callable(maxsize):
        foo = maxsize
        maxsize = None
        return decorator(foo)
    return decorator


@lru_cache
def sum(a: int, b: int) -> int:
    return a + b


@lru_cache
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@lru_cache(maxsize=3)
def multiply(a: int, b: int) -> int:
    return a * b


if __name__ == "__main__":
    assert sum(1, 2) == 3
    assert sum(3, 4) == 7

    assert multiply(1, 2) == 2
    assert multiply(3, 4) == 12

    assert sum_many(1, 2, c=3, d=4) == 10

    mocked_func = unittest.mock.Mock()
    mocked_func.side_effect = [1, 2, 3, 4]

    decorated = lru_cache(maxsize=2)(mocked_func)
    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 1
    assert decorated(3, 4) == 2
    assert decorated(3, 4) == 2
    assert decorated(5, 6) == 3
    assert decorated(5, 6) == 3
    assert decorated(1, 2) == 4
    assert mocked_func.call_count == 4
