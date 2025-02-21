import random
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from multiprocessing import Pool, Process, Queue, cpu_count
from multiprocessing import pool as thr_pool


def generate_data(n: int) -> list[int]:
    return [random.randint(0, 1000) for _ in range(n)]  # noqa: S311


def process_number(number: int) -> int:
    result = 1
    for i in range(2, number + 1):
        result *= i
    return result


def run_with_tread_pool(n: int, thread_pool_size: int = 5) -> list[int]:
    def collect_data(executor: ThreadPoolExecutor) -> list[int]:
        chunks = [n // thread_pool_size] * thread_pool_size
        for i in range(n % thread_pool_size):
            chunks[i] += 1

        futures = [
            executor.submit(generate_data, chunk)
            for chunk in chunks
        ]
        return list(chain.from_iterable(f.result() for f in futures))


    def proccess_data(executor: ThreadPoolExecutor, data: list[int]) -> list[int]:
        result = executor.map(process_number, data)
        return list(result)


    with ThreadPoolExecutor(max_workers=thread_pool_size) as executor:
        data = collect_data(executor)
        processed_data = proccess_data(executor, data)
        executor.shutdown(wait=False)
        return processed_data


def run_with_process_pool(n: int) -> list[int]:
    def collect_data(pool: thr_pool.Pool) -> list[int]:
        chunks = [[n // cpu_cores]] * cpu_cores
        for i in range(n % cpu_cores):
            chunks[i][0] += 1

        result = pool.starmap_async(generate_data, chunks)
        return list(chain(*result.get()))


    def proccess_data(pool: thr_pool.Pool, data: list[int]) -> list[int]:
        return pool.map(process_number, data)


    cpu_cores = cpu_count()
    with Pool(processes=cpu_cores) as pool:
        data = collect_data(pool)
        return proccess_data(pool, data)


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


def main(
        n: int,
        thread_pool_size: int = 8,
) -> None:
    run_thr_st_time = time.time()
    run_with_tread_pool(n, thread_pool_size=thread_pool_size)
    run_thr_result = time.time() - run_thr_st_time

    run_pr_st_time = time.time()
    run_with_process_pool(n)
    run_pr_result = time.time() - run_pr_st_time

    run_pr_s_st_time = time.time()
    run_with_single_processes(n)
    run_pr_s_result = time.time() - run_pr_s_st_time

    print(
        'threads', run_thr_result, '\n',
        'pr_pool', run_pr_result, '\n',
        'pr_single', run_pr_s_result
    )


if __name__ == "__main__":
    main(100_00)


