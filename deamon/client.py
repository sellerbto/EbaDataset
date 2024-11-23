from enum import Enum
import argparse
import socket


class CommandType(Enum):
    ADD = "add"
    REMOVE = "remove"
    LIST = "list"
    EXIT = "exit"

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def from_str(string: str) -> 'CommandType':
        return CommandType(string)


def send_command(cmd: CommandType, file_path=None) -> str:
    try:
        with socket.create_connection(("localhost", 9999)) as sock:
            message = cmd.value
            if file_path:
                message += f" {file_path}"
            sock.sendall(message.encode("utf-8"))

            response = sock.recv(4096).decode("utf-8")
            return response
    except ConnectionRefusedError as e:
        return str(e)


def main() -> None:
    parser = argparse.ArgumentParser(description="a client for managing a file tracking server")
    subparsers = parser.add_subparsers(title="commands", dest="command", required=True)

    add_parser = subparsers.add_parser(CommandType.ADD, help="add a tracking file")
    add_parser.add_argument("file_path", type=str, help="the full path to the tracking file")

    remove_parser = subparsers.add_parser(CommandType.REMOVE, help="remove a file from tracking")
    remove_parser.add_argument("file_path", type=str, help="the full path to the file to remove from tracking")

    list_parser = subparsers.add_parser(CommandType.LIST, help="list of all tracked files")

    exit_parser = subparsers.add_parser(CommandType.EXIT, help="stop server")

    args = parser.parse_args()
    print(send_command(CommandType.from_str(args.command), args.file_path if hasattr(args, 'file_path') else None))


if __name__ == "__main__":
    main()
