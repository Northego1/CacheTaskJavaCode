import re
import socket


def headers_to_dict(headers: bytes) -> dict[str, str]:
    headers_text = headers.decode()
    headers_dict = {}
    for line in headers_text.split("\n"):
        if ": " in line:
            key, value = line.split(": ", 1)
            headers_dict[key] = value
    return headers_dict


def request_google(start_string: str, host: str) -> dict[str, dict | str]:
    request = (
        f"{start_string}\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )

    with socket.create_connection((host, 80)) as sock:
        sock.sendall(request.encode())
        response = []
        while True:
            chunk = sock.recv(4096)
            if chunk:
                response.append(chunk)
            else:
                break
        response_text = b"".join(response)
        head, _, bod = response_text.partition(b"\r\n\r\n")
        headers = headers_to_dict(head)
        content_type = headers.get("Content-Type", None)
        if content_type:
            re_searched = re.search(r"charset=([\w-]+)", content_type)
            body_coding_type = re_searched.group(1) if re_searched else "UTF-8"
        else:
            body_coding_type = "UTF-8"

        return {
            "headers": headers,
            "body": bod.decode(body_coding_type),
        }

if __name__ == "__main__":
    request_google(
        start_string="GET / HTTP/1.1",
        host="www.google.com",
    )