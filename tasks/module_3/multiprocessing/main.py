import asyncio
import json
import random
import time
from typing import Self

import aiofiles
from pr_pool import RunWithProcessorPool
from processes import RunWithProcesses
from thread_pool import RunWithTreadPool


class ConcurentBase:
    def generate_data(self: Self, n: int) -> list[int]:  
        return [random.randint(0, 1000) for _ in range(n)]  # noqa: S311


    def process_number(self: Self, number: int) -> int:
        result = 1
        for i in range(2, number + 1):
            result *= i
        return result




async def main(
        n: int,
        thread_pool_size: int = 8,
        saving_path: str = './results.jsonl',
) -> None:
    cb = ConcurentBase()

    run_s_pr_time = time.time()
    result = [cb.process_number(num) for num in cb.generate_data(n)]
    run_s_pr_result = time.time()- run_s_pr_time

    run_thr_st_time = time.time()
    RunWithTreadPool(cb, thread_pool_size=thread_pool_size).run(n)
    run_thr_result = time.time() - run_thr_st_time

    run_pr_st_time = time.time()
    RunWithProcessorPool(cb).run(n)
    run_pr_pool_result = time.time() - run_pr_st_time

    run_pr_st_time = time.time()
    RunWithProcesses(cb).run(n)
    run_pr_result = time.time() - run_pr_st_time


    result = {
        "test_info": {
            "n": n,
            "thread_pool_size": thread_pool_size,
            "process_pool_size": "equal cpu cores",
            "processes_quantity": "equal cpu cores",
        },
        "test_results": {
            "SingleProcessResult": {
                "exec_time": round(run_s_pr_result, 5),
                "%": 0,
            },
            "ThreadPoolResult": {
                "exec_time": round(run_thr_result, 5),
                "%": round((run_s_pr_result / run_thr_result) * 100, 1),
            },
            "ProcessPoolResult": {
                "exec_time": round(run_pr_pool_result, 5),
                "%": round((run_s_pr_result / run_pr_pool_result) * 100, 1),
            },
            "ProcessResult": {
                "exec_time": round(run_pr_result, 5),
                "%": round((run_s_pr_result / run_pr_result) * 100, 1),
            },
        },
    }

    async with aiofiles.open(saving_path, "w", encoding="utf-8") as file:
        await file.write(json.dumps(result, indent=4))



if __name__ == "__main__":
    asyncio.run(main(100_000))


