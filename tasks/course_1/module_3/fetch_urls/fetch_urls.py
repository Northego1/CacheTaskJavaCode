import asyncio
import json
from pathlib import Path

import aiofiles
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError
from aiohttp.web_exceptions import HTTPException

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url"
]

sema = asyncio.Semaphore(5)


async def send_request(session: ClientSession, url: str) -> tuple:
    try:
        async with sema:
            response = await session.get(url)
    except ClientError:
        return (url, 0)
    except HTTPException:
        return (url, 1)
    return (url, response.status)


async def fetch_urls(urls: list[str], file_path: str) -> None:
    async with ClientSession() as session:
        tasks = [asyncio.create_task(send_request(session, url)) for url in urls]
        responses = await asyncio.gather(*tasks)
        fetched_dict = {resp[0]: resp[1] for resp in responses}

    async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
        await file.write(json.dumps(fetched_dict, indent=4))


if __name__ == "__main__":
    asyncio.run(fetch_urls(urls, "./results.jsonl"))
