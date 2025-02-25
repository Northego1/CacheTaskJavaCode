from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from main import ConcurentBase


class RunWithTreadPool:
    def __init__(self: Self, cb: "ConcurentBase", thread_pool_size: int = 8) -> None:
        self.cb = cb
        self.thread_pool_size = thread_pool_size


    def _processing(self: Self, chunk: int) -> list[int]:
            data = self.cb.generate_data(chunk)
            return [self.cb.process_number(num) for num in data]


    def run(self: Self, n: int) -> list[int]:
        chunks = [n // self.thread_pool_size] * self.thread_pool_size
        for i in range(n % self.thread_pool_size):
            chunks[i] += 1

        with ThreadPoolExecutor(max_workers=self.thread_pool_size) as executor:
            futures = [
                executor.submit(self._processing, chunk) for chunk in chunks
            ]
            result = list(chain(*[f.result() for f in futures]))
            executor.shutdown(wait=False)
            return result
