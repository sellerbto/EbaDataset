import os
import asyncio
import signal
import click
from dotenv import load_dotenv
from core.model import Command, AddCommand, RemoveCommand, CommandResult, TrackingResults, \
    ListTrackedResult, \
    parse_result, PingResult, SimpleCommand, CommandType
from core.transfer import read_json, write_json, get_pid

load_dotenv()
SOCKET_PATH = os.getenv("SOCKET_PATH", "var/file_tracker.sock")
PID_FILE = os.getenv("PID_FILE", "var/daemon.pid")


class FileTrackingClient:
    def __init__(self):
        if not os.path.exists(SOCKET_PATH):
            raise FileNotFoundError(f"Server socket not found at {SOCKET_PATH}. Is the server running?")

    @staticmethod
    async def send_command(command: Command) -> CommandResult:
        reader, writer = await asyncio.open_unix_connection(SOCKET_PATH)

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
    os.system(f"python3 server.py")
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
    """Status of file tracking server work."""
    client = FileTrackingClient()
    try:
        results: PingResult = asyncio.run(client.send_command(SimpleCommand(CommandType.PING)))
        click.echo(results.status_info)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("file_paths", nargs=-1, type=click.Path())
def add(file_paths: tuple) -> None:
    """Add files to tracking."""
    file_paths = list(file_paths)
    client = FileTrackingClient()
    try:
        results: TrackingResults = asyncio.run(client.send_command(AddCommand(file_paths)))
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
    client = FileTrackingClient()
    try:
        results: TrackingResults = asyncio.run(client.send_command(RemoveCommand(file_paths)))
        click.echo("Tracking stopped for the following files:")
        for result in results:
            click.echo(f"- {result.file_path}: {result.status}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command(name="list")
def get_list() -> None:
    """List all tracked files."""
    client = FileTrackingClient()
    try:
        result: ListTrackedResult = asyncio.run(client.send_command(SimpleCommand(CommandType.LIST)))
        click.echo("Currently tracked files:")
        for file_path in result.file_paths:
            click.echo(f"- {file_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    cli()
