from itertools import chain
from multiprocessing import Pool, cpu_count
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from main import ConcurentBase


class RunWithProcessorPool:
    def __init__(self: Self, cb: "ConcurentBase") -> None:
        self.cb = cb


    def _processing(self: Self, chunk: int) -> list[int]:
        data = self.cb.generate_data(chunk)
        return [self.cb.process_number(num) for num in data]


    def run(self: Self, n: int) -> list[int]:
        cpu_cores = cpu_count()
        chunks = [[n // cpu_cores] for _ in range(cpu_cores)]
        for i in range(n % cpu_cores):
            chunks[i][0] += 1

        with Pool(processes=cpu_cores) as pool:
            pr_result = pool.starmap_async(self._processing, chunks)
            return list(chain(*pr_result.get()))
