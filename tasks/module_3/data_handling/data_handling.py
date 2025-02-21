import asyncio
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from multiprocessing import Pool, Process, Queue, cpu_count

import aiofiles


def generate_data(n: int) -> list[int]:
    return [random.randint(0, 1000) for _ in range(n)]  # noqa: S311


def process_number(number: int) -> int:
    result = 1
    for i in range(2, number + 1):
        result *= i
    return result


def run_with_tread_pool(n: int, thread_pool_size: int = 5) -> list[int]:
    def processing(chunk: int) -> list[int]:
        data = generate_data(chunk)
        return [process_number(num) for num in data]

    result = []
    chunks = [n // thread_pool_size] * thread_pool_size
    for i in range(n % thread_pool_size):
        chunks[i] += 1

    with ThreadPoolExecutor(max_workers=thread_pool_size) as executor:
        futures = [
            executor.submit(processing, chunk) for chunk in chunks
        ]
        result = list(chain(*[f.result() for f in futures]))
        executor.shutdown(wait=False)
        return result


def _pool_process_processing(chunk: int) -> list[int]:
    data = generate_data(chunk)
    return [process_number(num) for num in data]

def run_with_process_pool(n: int) -> list[int]:
    cpu_cores = cpu_count()
    chunks = [[n // cpu_cores] for _ in range(cpu_cores)]
    for i in range(n % cpu_cores):
        chunks[i][0] += 1

    with Pool(processes=cpu_cores) as pool:
        pr_result = pool.starmap_async(_pool_process_processing, chunks)
        return list(chain(*pr_result.get()))


def run_with_single_processes(n: int) -> list[int]:
    def processing(chunk: int) -> None:
        data = generate_data(chunk)
        queue.put([process_number(num) for num in data])


    queue = Queue()
    result = []

    cpu_cores = cpu_count()
    chunks = [n // cpu_cores] * cpu_cores
    for i in range(n % cpu_cores):
        chunks[i] += 1

    processes: list[Process] = []
    for chunk in chunks:
        p = Process(target=processing, args=(chunk, ))
        p.start()
        processes.append(p)

    for _ in processes:
        result.extend(queue.get())

    for p in processes:
        p.join()

    return result


async def main(
        n: int,
        thread_pool_size: int = 8,
        saving_path: str = './results.json',
) -> None:
    run_s_pr_time = time.time()
    result = [process_number(num) for num in generate_data(n)]
    run_s_pr_result = time.time()- run_s_pr_time

    run_thr_st_time = time.time()
    run_with_tread_pool(n, thread_pool_size=thread_pool_size)
    run_thr_result = time.time() - run_thr_st_time

    run_pr_st_time = time.time()
    run_with_process_pool(n)
    run_pr_pool_result = time.time() - run_pr_st_time

    run_pr_st_time = time.time()
    run_with_single_processes(n)
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


