import json
from typing import Any, Awaitable, Callable

import aiohttp
import aiohttp.client_exceptions
import uvicorn


async def get_currency(
        currency: str,
        response: Callable[..., Awaitable[None]],
) -> None:
    url = f"https://api.exchangerate-api.com/v4/latest/{currency}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as resp:
                data = await resp.json()
                await response(
                    resp.status,
                    data,
                    {"Content-Type": "application/json"},
                )
    except aiohttp.client_exceptions.ClientError:
        await response(400, {"result": "error", "error_type": "unsupported_code"})



async def asgi_app(
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]] ,  # noqa: ARG001
        send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    async def response(
            status_code: int,
            body: Any,
            headers: dict[str, str] | None = None,
    ) -> None:
        if headers is None:
            headers = {}
        if isinstance(body, dict):
            headers["Content-Type"] = "application/json"
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            headers["Content-Type"] = "text/html"
            body = body.encode()
        else:
            headers["Content-Type"] = "application/octet-stream"

        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    (key.encode(), value.encode()) for \
                    key, value in headers.items()
                ],
            },
        )
        await send(
            {
                "type": "http.response.body",
                "body": body,
            },
        )

    if scope["type"] == "http":
        currency = scope["path"].split("/")[-1]
        if len(currency) != 3:
            await response(404, {"result": "error", "error_type": "unsupported_code"})
        else:
            await get_currency(currency, response)


if __name__ == "__main__":
    uvicorn.run("currency_proxy:asgi_app", reload=True)


# http://127.0.0.1:8000/USD     ok
# http://127.0.0.1:8000/WWW     {"result": "error", "error_type": "unsupported_code"}
# http://127.0.0.1:8000/AAAA    {"result": "error", "error_type": "unsupported_code"}
# http://127.0.0.1:8000/АРБУЗ14   {"result": "error", "error_type": "unsupported_code"}