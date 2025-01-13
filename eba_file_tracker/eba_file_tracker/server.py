import os
import asyncio
import signal
import logging
import argparse
from dotenv import load_dotenv
from pathlib import Path
from .core.tracker import DirectoryTrackerManager
from .core.models.server import ServerConfiguration
from .core.models.command import CommandType, AddCommand, parse_command
from .core.models.result import ListTrackingInfoResult, PingResult
from .core.communication.json_transfer import read_json, write_json
from .core.communication.system import daemonize, clear_files, get_tcp_ip_socket

load_dotenv(Path("eba_file_tracker") / "var" / ".env")
PID_FILE = os.getenv("PID_FILE")
SOCKET_FILE = os.getenv("SOCKET_FILE")
HOST_NAME = os.getenv("HOST_NAME")
HOST_PORT = int(os.getenv("HOST_PORT"))
LOG_FILE = os.getenv("LOG_FILE")


def clear_runtime_files() -> None:
    clear_files([PID_FILE, SOCKET_FILE])


def set_up_logging(release_version: bool) -> None:
    handlers = [logging.FileHandler(LOG_FILE)]  # logging to file
    if not release_version:
        handlers.append(logging.StreamHandler())  # logging to console
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


class FileTrackingServer:
    def __init__(self, configuration: ServerConfiguration) -> None:
        self.configuration = configuration
        self.tracker_manager: DirectoryTrackerManager = None
        self.server: asyncio.Server = None

        clear_runtime_files()
        if configuration.release_version:
            daemonize()
        set_up_logging(configuration.release_version)

        self.pid = os.getpid()
        with open(PID_FILE, "w") as f:
            f.write(str(self.pid))

        self.configuration.set_dynamic(self.pid, HOST_NAME, HOST_PORT)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        addr = None
        try:
            addr = writer.get_extra_info('socket') if self.configuration.use_unix_optimization \
                else writer.get_extra_info('peername')
            request_data = await read_json(reader)
            logging.info(f"Received from {addr} {request_data}")
            command = parse_command(request_data)

            match command.type:
                case CommandType.ADD:
                    command: AddCommand
                    result = ListTrackingInfoResult(
                        [self.tracker_manager.start_watching(file_path) for file_path in command.file_paths]
                    )
                case CommandType.REMOVE:
                    command: AddCommand
                    result = ListTrackingInfoResult(
                        [self.tracker_manager.stop_watching(file_path) for file_path in command.file_paths]
                    )
                case CommandType.LIST:
                    result = self.tracker_manager.list_watched_files()
                case CommandType.PING:
                    result = PingResult(self.configuration)
                case _:
                    raise ValueError(f"Unknown command {command}")

            response_data = result.to_json_data()
            logging.info(f"Response for {addr} {response_data}")
            await write_json(writer, response_data)
        except Exception as e:
            logging.error(f"Error while handling client {addr if addr else '-'}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def run(self) -> None:
        await self._start_server()
        stop_event = asyncio.Event()

        def handle_signal(s: signal.Signals) -> None:
            logging.info(f"Received exit signal {s.name}. Stopping server...")
            stop_event.set()

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: handle_signal(sig))

        await stop_event.wait()
        await self._stop_server()

    async def _start_server(self) -> None:
        self.tracker_manager = DirectoryTrackerManager()
        self.server = await asyncio.start_unix_server(self.handle_client, path=SOCKET_FILE) \
            if self.configuration.use_unix_optimization \
            else await asyncio.start_server(self.handle_client, sock=get_tcp_ip_socket(HOST_NAME, HOST_PORT))

        extra_info = f" on {HOST_NAME}:{HOST_PORT}" if not self.configuration.use_unix_optimization else ""
        logging.info(f"Server started with a PID={self.pid}{extra_info}, {self.configuration}")

    async def _stop_server(self) -> None:
        self.tracker_manager.stop_all_watching()
        clear_runtime_files()
        self.server.close()
        await self.server.wait_closed()
        logging.info("Server stopped.")


def main() -> None:
    """Run the file tracking server."""
    parser = argparse.ArgumentParser(description="File tracking server.")

    parser.add_argument(
        "-ux", "--unix-optimization",
        action="store_true",
        help="uses UDS for server communication, otherwise TCP/IP. Optimization only works for UNIX"
    )

    parser.add_argument(
        "-rl", "--release",
        action="store_true",
        help="disable console logging and daemonize the server"
    )

    configuration = ServerConfiguration.parse(parser)
    server = FileTrackingServer(configuration)

    try:
        asyncio.run(server.run())
    except Exception as e:
        logging.error(f"Server error: {e}")


if __name__ == "__main__":
    main()
