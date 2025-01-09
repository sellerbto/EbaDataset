import os
import sys
import asyncio
import signal
import logging
from dotenv import load_dotenv
from core.tracker import DirectoryTrackerManager
from core.model import CommandType, AddCommand, TrackingResults, ListTrackedResult, \
    parse_command, PingResult
from core.transfer import read_json, write_json, get_pid

# Load environment variables
load_dotenv()
SOCKET_PATH = os.getenv("SOCKET_PATH", "var/file_tracker.sock")
LOG_FILE = os.getenv("LOG_FILE", "var/server.log")
PID_FILE = os.getenv("PID_FILE", "var/daemon.pid")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Логирование в файл
        logging.StreamHandler()  # Логирование в консоль
    ]
)


def daemonize() -> None:
    """Making the process a daemon"""
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

    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


class FileTrackingServer:
    def __init__(self):
        daemonize()
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
                    result = TrackingResults(
                        [self.tracker_manager.start_watching(file_path) for file_path in command.file_paths]
                        )
                case CommandType.REMOVE:
                    command: AddCommand
                    result = TrackingResults(
                        [self.tracker_manager.stop_watching(file_path) for file_path in command.file_paths]
                        )
                case CommandType.LIST:
                    result = ListTrackedResult(self.tracker_manager.list_watched_files())
                case CommandType.PING:
                    result = PingResult(f"The tracking server is running with a PID={get_pid(PID_FILE)}")
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


def run_server() -> None:
    """Run the file tracking server."""
    server = FileTrackingServer()

    def handle_signal(signal_number, frame) -> None:
        logging.info("Stopping server...")
        loop = asyncio.get_event_loop()
        loop.create_task(server.stop_server())
        loop.stop()  # todo не работает
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        asyncio.run(server.start_server())
    except Exception as e:
        logging.error(f"Error starting server: {e}")


if __name__ == "__main__":
    run_server()
