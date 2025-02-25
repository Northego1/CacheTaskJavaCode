from itertools import chain
from multiprocessing import Pool, Process, Queue, cpu_count
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from main import ConcurentBase


class RunWithProcesses:
    def __init__(self: Self, cb: "ConcurentBase") -> None:
        self.cb = cb
        self.queue = Queue()


    def _processing(self: Self, chunk: int) -> None:
        data = self.cb.generate_data(chunk)
        self.queue.put([self.cb.process_number(num) for num in data])

    def run(self: Self, n: int) -> list[int]:
        result = []

        cpu_cores = cpu_count()
        chunks = [n // cpu_cores] * cpu_cores
        for i in range(n % cpu_cores):
            chunks[i] += 1

        processes: list[Process] = []
        for chunk in chunks:
            p = Process(target=self._processing, args=(chunk, ))
            p.start()
            processes.append(p)

        for _ in processes:
            result.extend(self.queue.get())

        for p in processes:
            p.join()

        return result
