import os
import asyncio
import signal
import click
from typing import Any
from dotenv import load_dotenv
from core.model import Command, AddCommand, RemoveCommand, CommandResult, TrackingResults, ListTrackedResult, \
    parse_result, PingResult, SimpleCommand, CommandType
from core.transfer import read_json, write_json, read_from_json, write_to_json, get_pid

load_dotenv("var/.env")
PID_FILE = os.getenv("PID_FILE")
SOCKET_FILE = os.getenv("SOCKET_FILE")
HOST_NAME = os.getenv("HOST_NAME")
HOST_PORT = int(os.getenv("HOST_PORT"))
CLIENT_STATE_FILE = os.getenv("CLIENT_STATE_FILE")


class State:
    def __init__(self, data: dict[str, Any]):
        self.state = data

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
            write_to_json(CLIENT_STATE_FILE, dict())

        return State(read_from_json(CLIENT_STATE_FILE))

    def write(self) -> None:
        write_to_json(CLIENT_STATE_FILE, self.state)


state: State = None


async def send_command(command: Command) -> CommandResult:
    reader, writer = await asyncio.open_unix_connection(SOCKET_FILE) \
        if state.use_unix_optimization \
        else await asyncio.open_connection(HOST_NAME, HOST_PORT)

    try:
        await write_json(writer, command.to_dict())
        data = await read_json(reader)
        result = parse_result(command.type, data)
        return result
    finally:
        writer.close()
        await writer.wait_closed()


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
    if no_optimization:
        state.use_unix_optimization = False

    start_cmd = "python3 server.py -rl"
    if state.use_unix_optimization:
        start_cmd += " -ux"

    os.system(start_cmd)
    click.echo("Server started.")


@cli.command()
def stop() -> None:
    """Stop the file tracking server."""
    # if not os.path.exists(PID_FILE):
    #     # send ping
    #     raise FileNotFoundError(
    #         f"The ID of the process running the server was not detected at {PID_FILE}. Is the server running?"
    # )
    try:
        state.clear()
        pid = get_pid(PID_FILE)
        os.kill(pid, signal.SIGTERM)
        click.echo("Server stopped.")
    except FileNotFoundError:
        click.echo("PID file not found.", err=True)
    except ProcessLookupError:
        click.echo("Process not found.", err=True)


@cli.command()
def status() -> None:
    """The status of the file tracking server."""
    try:
        results: PingResult = asyncio.run(send_command(SimpleCommand(CommandType.PING)))
        click.echo(results.status_info)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("file_paths", nargs=-1, type=click.Path())
def add(file_paths: tuple) -> None:
    """Add files to tracking."""
    file_paths = list(file_paths)

    try:
        results: TrackingResults = asyncio.run(send_command(AddCommand(file_paths)))
        click.echo("Tracking started for the following files:")
        for result in results:
            click.echo(f"- {result.file_path}: {result.status}")  # todo response formatter
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("file_paths", nargs=-1, type=click.Path())
def remove(file_paths: tuple) -> None:
    """Remove files from tracking."""
    file_paths = list(file_paths)
    try:
        results: TrackingResults = asyncio.run(send_command(RemoveCommand(file_paths)))
        click.echo("Tracking stopped for the following files:")
        for result in results:
            click.echo(f"- {result.file_path}: {result.status}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command(name="list")
def get_list() -> None:
    """List all tracked files."""
    try:
        result: ListTrackedResult = asyncio.run(send_command(SimpleCommand(CommandType.LIST)))
        click.echo("Currently tracked files:")
        for file_path in result.file_paths:
            click.echo(f"- {file_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


def main() -> None:
    global state

    try:
        state = State.read()
        cli()
    except Exception as e:
        click.echo(f"Client error: {e}", err=True)
    finally:
        state.write()


if __name__ == "__main__":
    main()
