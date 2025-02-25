import datetime
import time
from typing import Any, Callable

import redis as r


def single(max_processing_time: datetime.timedelta) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def _is_already_running() -> bool:
            flag = redis.get("single_running")
            return bool(flag)


        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not _is_already_running():
                redis.setex(
                    "single_running",
                    int(max_processing_time.total_seconds()),
                    "1",
                )
                result = func(*args, **kwargs)
                redis.delete("single_running")
                return result
            raise RuntimeError("single already running")
        return wrapper
    return decorator


@single(max_processing_time=datetime.timedelta(minutes=2))
def process_transaction():
    time.sleep(5)


def main() -> None:
    try:
        process_transaction()
    except RuntimeError:
        print("already running")


if __name__ == "__main__":
    redis = r.Redis()
    main()
