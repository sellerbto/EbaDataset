import os
import sys
import socket
from pathlib import Path


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


def normalize_env_paths(env_file: str) -> None:
    """Read the .env file, normalize the paths and save"""
    env_vars = {}

    with open(env_file, 'r') as file:
        for line in file:
            if line.strip() and '=' in line:  # skip empty string and comment
                key, value = map(str.strip, line.split('=', 1))
                if ('/' in value or '\\' in value) and ('http' not in value or ':' not in value):  # look like file path
                    normalized_path = Path(value).as_posix().replace('\\', '/') \
                        if os.name != 'nt' \
                        else Path(value).as_posix().replace('/', '\\')
                    env_vars[key] = normalized_path
                else:
                    env_vars[key] = value

    with open(env_file, 'w') as file:
        for key, value in env_vars.items():
            file.write(f"{key}={value}\n")


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
