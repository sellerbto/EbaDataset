import os
import sys
import json
import socket
import asyncio
from .models.base import JsonData


def daemonize() -> None:
    """Making the process a daemon."""
    if os.fork() > 0:
        sys.exit(0)

    os.setsid()

    if os.fork() > 0:
        sys.exit(0)

    sys.stdout.flush()
    sys.stderr.flush()
    with open(os.devnull, 'wb', 0) as null_out:
        os.dup2(null_out.fileno(), sys.stdout.fileno())
        os.dup2(null_out.fileno(), sys.stderr.fileno())


async def read_json(reader: asyncio.StreamReader) -> JsonData:
    data = b""
    while not reader.at_eof():
        chunk = await reader.read(1024)
        data += chunk
    return json.loads(data.decode("utf-8"))


async def write_json(writer: asyncio.StreamWriter, json_data: JsonData) -> None:
    json_data = json.dumps(json_data)
    writer.write(json_data.encode("utf-8"))
    await writer.drain()
    writer.write_eof()


def read_json_from_file(file_path: str) -> JsonData:
    with open(file_path, "r") as file:
        json_data = json.load(file)
        return json_data


def write_json_to_file(file_path: str, json_data: JsonData) -> None:
    with open(file_path, "w") as file:
        json.dump(json_data, file, indent=4)


def get_pid(pid_file_path: str) -> int:
    if not os.path.exists(pid_file_path):
        raise FileNotFoundError(pid_file_path)

    with open(pid_file_path, "r") as pid_file:
        return int(pid_file.read().strip())


def is_process_running(pid: int) -> None:
    try:
        os.kill(pid, 0)  # doesn't kill process, but only checks it
    except OSError:
        return False
    else:
        return True


def clear_files(file_paths: list[str] | str) -> None:
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    for file in file_paths:
        if os.path.exists(file):
            os.remove(file)


def get_tcp_ip_socket(host: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((host, port))
    sock.listen(5)
    sock.setblocking(False)

    return sock
