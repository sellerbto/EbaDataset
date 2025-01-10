import os
import asyncio
import signal
import click
from dotenv import load_dotenv
from core.model import Command, AddCommand, RemoveCommand, CommandResult, TrackingResults, ListTrackedResult, \
    parse_result, PingResult, SimpleCommand, CommandType
from core.transfer import read_json, write_json, get_pid

load_dotenv("var/.env")
PID_FILE = os.getenv("PID_FILE")
SOCKET_FILE = os.getenv("SOCKET_FILE")
HOST_NAME = os.getenv("HOST_NAME")
HOST_PORT = int(os.getenv("HOST_PORT"))

use_unix_optimization = os.name == 'posix'


# if not os.path.exists(PID_FILE):
#     raise FileNotFoundError(
#         f"The ID of the process running the server was not detected at {PID_FILE}. Is the server running?"
#     )
# if not os.path.exists(SOCKET_FILE):
#     raise FileNotFoundError(f"The server socket not found at {SOCKET_FILE}. Is the server running?")


async def send_command(command: Command) -> CommandResult:
    reader, writer = await asyncio.open_unix_connection(SOCKET_FILE) \
        if use_unix_optimization \
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
def start() -> None:
    """Start the file tracking server."""
    start_cmd = "python3 server.py"
    if use_unix_optimization:
        start_cmd += " -ux"
    os.system(start_cmd)
    click.echo("Server started.")


@cli.command()
def stop() -> None:
    """Stop the file tracking server."""
    try:
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
    try:
        cli()
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    main()
