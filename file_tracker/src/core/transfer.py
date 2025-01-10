import os
import json
import socket
import asyncio
from typing import Any


async def write_json(writer: asyncio.StreamWriter, data: dict[str, Any]) -> None:
    json_data = json.dumps(data)
    writer.write(json_data.encode("utf-8"))
    await writer.drain()
    writer.write_eof()


async def read_json(reader: asyncio.StreamReader) -> dict[str, Any]:
    data = b""
    while not reader.at_eof():
        chunk = await reader.read(1024)
        data += chunk
    return json.loads(data.decode("utf-8"))


def get_pid(pid_file_path: str) -> int:
    if not os.path.exists(pid_file_path):
        raise FileNotFoundError(pid_file_path)

    with open(pid_file_path, "r") as pid_file:
        return int(pid_file.read().strip())


def get_tcp_ip_socket(host: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((host, port))
    sock.listen(5)
    sock.setblocking(False)

    return sock
