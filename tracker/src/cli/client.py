import os
import asyncio
import click
from dotenv import load_dotenv
from tracker.src.shared.model import Command, AddCommand, RemoveCommand, ListCommand, CommandResult, TrackingResults, ListTrackedResult, \
    parse_result
from tracker.src.shared.json_transfer import read_json, write_json

# Load environment variables
load_dotenv()
SOCKET_PATH = os.getenv("SOCKET_PATH", "/tmp/file_tracker.sock")


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
        result: ListTrackedResult = asyncio.run(client.send_command(ListCommand()))
        click.echo("Currently tracked files:")
        for file_path in result.file_paths:
            click.echo(f"- {file_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
def start() -> None:
    """Start the file tracking server."""
    os.system(f"python server.py start")
    click.echo("Server started.")


@cli.command()
def stop() -> None:
    """Stop the file tracking server."""
    os.system(f"python server.py stop")
    click.echo("Server stopped.")


if __name__ == "__main__":
    cli()
