import datetime
import multiprocessing
import time
from functools import wraps
from queue import Empty
from typing import Any, Callable

from redis import Redis, lock

redis = Redis()

def single(max_processing_time: datetime.timedelta) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        lck = lock.Lock(
            redis,
            "single_running_lock",
            timeout=max_processing_time.total_seconds(),
        )
        queue = multiprocessing.Queue()
        def _pr_func(
                foo: Callable[..., Any],
                queue: multiprocessing.Queue,
                args: tuple, kwargs: dict,
        ) -> None:
            result = foo(*args, **kwargs)
            queue.put(result)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not lck.acquire(blocking=False):
                raise RuntimeError("single already running")
            try:
                pr = multiprocessing.Process(target=_pr_func, args=(func, queue, args, kwargs))
                pr.start()
                try:
                    result = queue.get(timeout=max_processing_time.total_seconds())
                except Empty:
                    pr.terminate()
                    raise RuntimeError("unfe")
            finally:
                lck.release()
            return result
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
    main()
