import asyncio
import json
from typing import AsyncGenerator

import aiofiles
from aiofiles.threadpool.text import AsyncTextIOWrapper
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError
from aiohttp.web_exceptions import HTTPException

sema = asyncio.Semaphore(5)

async def request_manager(
        session: ClientSession,
        url: str,
        file_write_gen: AsyncGenerator[None, dict[str, int]],
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

    await file_write_gen.asend(write_line)


async def file_writer(file_path: str) -> AsyncGenerator[None, dict[str, int]]:
    async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
        try:
            while True:
                line = yield None
                await file.write(json.dumps(line, indent=4) + "\n")
        finally:
            await file.flush()
            await file.close()



async def fetch_urls(
        file: AsyncTextIOWrapper,
        file_path: str = "./result.jsonl",
) -> None:
    tasks = []
    async with ClientSession() as session:
        write_gen = file_writer(file_path)
        await anext(write_gen)

        async for line in file:
            url = line.strip()
            tasks.append(asyncio.create_task(request_manager(session, url, write_gen)))

        await asyncio.gather(*tasks)
        await write_gen.aclose()



async def main() -> None:
    async with aiofiles.open("./urls.txt", "r", encoding="utf-8") as file:  # noqa: UP015
        await fetch_urls(file)


if __name__ == "__main__":
    asyncio.run(main())
