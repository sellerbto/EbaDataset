import os
import asyncio
import signal
import click
from dotenv import load_dotenv
from pathlib import Path
from .core.models.base import DictJsonData
from .core.models.command import Command, AddCommand, RemoveCommand, SimpleCommand, CommandType
from .core.models.result import CommandResult, ListTrackingInfoResult, ListTrackedInfoResult, PingResult, parse_result
from .core.communication.json_transfer import read_json, write_json, read_json_from_file, write_json_to_file
from .core.communication.system import get_pid, is_process_running
from .response import ResponseFormatter

load_dotenv(Path("eba_file_tracker") / "var" / ".env")
PID_FILE = os.getenv("PID_FILE")
SOCKET_FILE = os.getenv("SOCKET_FILE")
HOST_NAME = os.getenv("HOST_NAME")
HOST_PORT = int(os.getenv("HOST_PORT"))
CLIENT_STATE_FILE = os.getenv("CLIENT_STATE_FILE")


class State:
    def __init__(self, json_data: DictJsonData):
        self.state = json_data

    @property
    def use_unix_optimization(self) -> bool:
        if 'use_unix_optimization' not in self.state:
            self.use_unix_optimization = os.name == 'posix'
        return self.state['use_unix_optimization']

    @use_unix_optimization.setter
    def use_unix_optimization(self, value: bool) -> None:
        self.state['use_unix_optimization'] = value

    def clear(self) -> None:
        self.state = dict()

    @staticmethod
    def read() -> 'State':
        if not os.path.exists(CLIENT_STATE_FILE):
            write_json_to_file(CLIENT_STATE_FILE, dict())

        return State(read_json_from_file(CLIENT_STATE_FILE))

    def write(self) -> None:
        write_json_to_file(CLIENT_STATE_FILE, self.state)


state: State = None


async def send_command(command: Command) -> CommandResult:
    reader, writer = await asyncio.open_unix_connection(SOCKET_FILE) \
        if state.use_unix_optimization \
        else await asyncio.open_connection(HOST_NAME, HOST_PORT)

    try:
        await write_json(writer, command.to_json_data())
        json_data = await read_json(reader)
        result = parse_result(command.type, json_data)
        return result
    finally:
        writer.close()
        await writer.wait_closed()


def send_ping() -> PingResult:
    """Send ping command to the server."""
    return asyncio.run(send_command(SimpleCommand(CommandType.PING)))


def slim_ping() -> bool:
    """Simplified server work check."""
    return os.path.exists(PID_FILE) and is_process_running(get_pid(PID_FILE))


@click.group()
def cli():
    """A client for managing a file tracking server."""
    pass


@cli.command()
@click.option(
    '-no', '--no-optimization', is_flag=True,
    help="Don't use UNIX optimizations, even if they are available."
)
def start(no_optimization: bool) -> None:
    """Start the file tracking server."""
    if slim_ping():
        send_ping()
        click.echo("Server is already working")
        return

    if no_optimization:
        state.use_unix_optimization = False

    server_path = Path("eba_file_tracker.server")
    start_cmd = f"python3 -m {server_path} -rl"
    if state.use_unix_optimization:
        start_cmd += " -ux"

    os.system(start_cmd)

    ping_result = send_ping()
    click.echo("Server start work with configuration:")
    click.echo(ResponseFormatter.make_from_configuration(ping_result.configuration))


@cli.command()
def stop() -> None:
    """Stop the file tracking server."""
    if not slim_ping():
        click.echo("Server is not running")
        return

    send_ping()
    state.clear()
    pid = get_pid(PID_FILE)
    os.kill(pid, signal.SIGTERM)
    click.echo("Server stopped")


@cli.command()
def status() -> None:
    """The status of the file tracking server."""
    if not slim_ping():
        click.echo("Server is not running")
        return

    ping_result = send_ping()
    click.echo("Server is working with configuration:")
    click.echo(ResponseFormatter.make_from_configuration(ping_result.configuration))


@cli.command()
@click.argument("file_paths", nargs=-1, type=click.Path())
def add(file_paths: tuple) -> None:
    """Add files to tracking."""
    if not slim_ping():
        click.echo("Server is not running")
        return

    file_paths = list(file_paths)
    results: ListTrackingInfoResult = asyncio.run(send_command(AddCommand(file_paths)))
    click.echo(ResponseFormatter.make_from_add(results))


@cli.command()
@click.argument("file_paths", nargs=-1, type=click.Path())
def remove(file_paths: tuple) -> None:
    """Remove files from tracking."""
    if not slim_ping():
        click.echo("Server is not running")
        return

    file_paths = list(file_paths)
    results: ListTrackingInfoResult = asyncio.run(send_command(RemoveCommand(file_paths)))
    click.echo(ResponseFormatter.make_from_remove(results))


@cli.command(name="list")
def get_list() -> None:
    """List all tracked files."""
    if not slim_ping():
        click.echo("Server is not running")
        return

    results: ListTrackedInfoResult = asyncio.run(send_command(SimpleCommand(CommandType.LIST)))
    click.echo(ResponseFormatter.make_from_list(results))


def main() -> None:
    global state
    state = State.read()

    try:
        cli()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
    finally:
        state.write()


if __name__ == "__main__":
    main()
