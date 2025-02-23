import asyncio

import aiohttp
from aiohttp.http import HttpVersion


async def request_google(start_string: str, host: str) -> int:
    method, path, http_v = start_string.split()
    http_v_major, http_v_minor = map(int, http_v.split("/")[1].split("."))
    http_version = HttpVersion(http_v_major, http_v_minor)

    async with aiohttp.request(
        method=method,
        url=f"https://{host}{path}",
        version=http_version,
    ) as response:
        return response.status



if __name__ == "__main__":
    asyncio.run(request_google(
        start_string="GET / HTTP/1.1",
        host='www.google.com',
    )) 