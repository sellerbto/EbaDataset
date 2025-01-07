import os
import sys
import asyncio
import signal
import logging
import click
from dotenv import load_dotenv
from tracker import DirectoryTrackerManager
from tracker.src.shared.model import CommandType, AddCommand, ListCommand, TrackingResults, ListTrackedResult, parse_command
from tracker.src.shared.json_transfer import read_json, write_json

# Load environment variables
load_dotenv()
SOCKET_PATH = os.getenv("SOCKET_PATH", "/tmp/file_tracker.sock")
LOG_FILE = os.getenv("LOG_FILE", "../server.log")
PID_FILE = os.getenv("PID_FILE", "/tmp/daemon.pid")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),     # Логирование в файл
        logging.StreamHandler()           # Логирование в консоль
    ]
)


def daemonize():
    """Делаем процесс демоном"""
    # Первый fork
    if os.fork() > 0:
        sys.exit(0)

    # Отделение от управляющего терминала
    os.setsid()

    # Второй fork
    if os.fork() > 0:
        sys.exit(0)

    # Перенаправляем стандартные потоки в /dev/null
    sys.stdout.flush()
    sys.stderr.flush()
    with open(os.devnull, 'wb', 0) as null_out:
        os.dup2(null_out.fileno(), sys.stdout.fileno())
        os.dup2(null_out.fileno(), sys.stderr.fileno())

    # Записываем PID в PID-файл
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


class FileTrackingServer:
    def __init__(self):
        # daemonize()
        self.tracker_manager = DirectoryTrackerManager()
        self.server = None
        self.is_running = False

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            data = await read_json(reader)
            command = parse_command(data)

            match command.type:
                case CommandType.ADD:
                    command: AddCommand
                    result = TrackingResults([self.tracker_manager.start_watching(file_path) for file_path in command.file_paths])
                case CommandType.REMOVE:
                    command: AddCommand
                    result = TrackingResults([self.tracker_manager.stop_watching(file_path) for file_path in command.file_paths])
                case CommandType.LIST:
                    command: ListCommand
                    result = ListTrackedResult(self.tracker_manager.list_watched_files())
                case _:
                    raise ValueError(f"Unknown command {command}")

            await write_json(writer, result.to_dict())
        except Exception as e:
            logging.error(f"Error handling client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def start_server(self):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        self.server = await asyncio.start_unix_server(self.handle_client, path=SOCKET_PATH)
        self.is_running = True

        logging.info("Server started.")
        async with self.server:
            await self.server.serve_forever()

    async def stop_server(self):
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            self.tracker_manager.stop_all_watching()
            self.is_running = False

        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        logging.info("Server stopped.")


@click.group()
def cli():
    "File Tracking Server Management."
    pass


@cli.command()
def start():
    "Start the file tracking server."
    server = FileTrackingServer()

    def handle_signal(signal_number, frame):
        logging.info("Stopping server...")
        loop = asyncio.get_event_loop()
        loop.create_task(server.stop_server())
        loop.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        asyncio.run(server.start_server())
    except Exception as e:
        logging.error(f"Error starting server: {e}")


@cli.command()
def stop():
    """Stop the file tracking server."""
    try:
        with open(PID_FILE, "r") as pid_file:
            pid = int(pid_file.read().strip())
        os.kill(pid, signal.SIGTERM)
        click.echo("Server stopped.")
    except FileNotFoundError:
        click.echo("PID file not found. Is the server running?", err=True)
    except ProcessLookupError:
        click.echo("Process not found. Is the server running?", err=True)


if __name__ == "__main__":
    cli()
