from deamon.base import CommandType, TrackingResult, TrackingStatus, ResponseFormatter
import argparse
import socket
import os


def send_command(cmd: CommandType, file_path=None) -> str:
    if file_path and not os.path.exists(file_path):
        return ResponseFormatter.make(cmd, TrackingResult(TrackingStatus.NOT_FOUND, file_path))

    try:
        with socket.create_connection(("localhost", 9998)) as sock:
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

    add_parser = subparsers.add_parser("add", help="add a tracking file")
    add_parser.add_argument("file_path", type=str, help="the full path to the tracking file")

    remove_parser = subparsers.add_parser("remove", help="remove a file from tracking")
    remove_parser.add_argument("file_path", type=str, help="the full path to the file to remove from tracking")

    list_parser = subparsers.add_parser("list", help="list of all tracked files")

    exit_parser = subparsers.add_parser("exit", help="stop server")

    args = parser.parse_args()
    response = send_command(CommandType(args.command), args.file_path if hasattr(args, 'file_path') else None)
    print(response)


if __name__ == "__main__":
    main()
