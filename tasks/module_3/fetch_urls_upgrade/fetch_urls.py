import asyncio
import json
from typing import AsyncGenerator

import aiofiles
from aiofiles.threadpool.text import AsyncTextIOWrapper
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError
from aiohttp.web_exceptions import HTTPException


async def request_manager(
        session: ClientSession,
        url: str,
        sema: asyncio.Semaphore,
        queue: asyncio.Queue,
    ) -> None:
    try:
        async with sema:
            response = await session.get(url)
        if 200 <= response.status < 300:
            write_line = {url: await response.json()}
        else:
            write_line = {url: response.status}
    except ClientError:
        write_line = {url: 0}
    except HTTPException:
        write_line = {url: 0}

    await queue.put(write_line)


async def file_writer(queue: asyncio.Queue, file_path: str) -> None:
    async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
        while True:
            line = await queue.get()
            if line is None:
                break
            await file.write(json.dumps(line, indent=4) + "\n")
            queue.task_done()


async def fetch_urls(
        file: AsyncTextIOWrapper,
        file_path: str = "./result.jsonl",
        tasks_limit: int = 5,
) -> None:
    queue = asyncio.Queue()
    sema = asyncio.Semaphore(tasks_limit)
    active_tasks = set()
    async with ClientSession() as session:
        writer_task = asyncio.create_task(file_writer(queue, file_path))

        async for line in file:
            url = line.strip()
            active_tasks.add(
                asyncio.create_task(request_manager(session, url, sema, queue))
            )
            while len(active_tasks) >= tasks_limit:
                done, _ = await asyncio.wait(active_tasks, return_when=asyncio.FIRST_COMPLETED)
                active_tasks -= set(done)
        await asyncio.gather(*active_tasks)
        await queue.put(None)
        await writer_task


async def main() -> None:
    async with aiofiles.open("./urls.txt", "r", encoding="utf-8") as file:  # noqa: UP015
        await fetch_urls(file)


if __name__ == "__main__":
    asyncio.run(main())
