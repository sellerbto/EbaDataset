from typing import Protocol, Any
from enum import Enum, auto


class CommandType(Enum):
    ADD = 'add'
    REMOVE = 'remove'
    LIST = 'list'
    PING = 'ping'

    @staticmethod
    def parse(data: dict[str, Any]) -> 'CommandType':
        value = data['command']
        match value:
            case CommandType.ADD.value:
                return CommandType.ADD
            case CommandType.REMOVE.value:
                return CommandType.REMOVE
            case CommandType.LIST.value:
                return CommandType.LIST
            case CommandType.PING.value:
                return CommandType.PING
            case _:
                raise ValueError(f"Unexpected value {value}")


class Command(Protocol):
    """Base class for request to server"""

    @property
    def type(self) -> CommandType:
        pass

    def to_dict(self) -> dict[str, Any]:
        pass

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'Command':
        pass


class AddCommand(Command):
    def __init__(self, file_paths: list[str]) -> None:
        self.file_paths: list[str] = file_paths

    @property
    def type(self) -> CommandType:
        return CommandType.ADD

    def to_dict(self) -> dict[str, Any]:
        return {
            'command': self.type.value,
            'file_paths': self.file_paths,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'AddCommand':
        return AddCommand(data['file_paths'])


class RemoveCommand(Command):
    def __init__(self, file_paths: list[str]) -> None:
        self.file_paths: list[str] = file_paths

    @property
    def type(self) -> CommandType:
        return CommandType.REMOVE

    def to_dict(self) -> dict[str, Any]:
        return {
            'command': self.type.value,
            'file_paths': self.file_paths,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'RemoveCommand':
        return RemoveCommand(data['file_paths'])


class SimpleCommand(Command):
    def __init__(self, cmd_type: CommandType):
        self.cmd_type: CommandType = cmd_type

    @property
    def type(self) -> CommandType:
        return self.cmd_type

    def to_dict(self) -> dict[str, Any]:
        return {
            'command': self.type.value,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'SimpleCommand':
        return SimpleCommand(CommandType.parse(data))


def parse_command(data: dict[str, Any]) -> 'Command':
    cmd_type = CommandType.parse(data)
    match cmd_type:
        case CommandType.ADD:
            return AddCommand.from_dict(data)
        case CommandType.REMOVE:
            return RemoveCommand.from_dict(data)
        case CommandType.LIST | CommandType.PING:
            return SimpleCommand.from_dict(data)
        case _:
            raise ValueError()


class TrackingStatus(Enum):
    IN_PROGRESS = auto()
    COMPLETED = auto()
    ALREADY = auto()
    NOT_FOUND = auto()

    @staticmethod
    def parse(data: dict[str, Any]) -> 'TrackingStatus':
        value = data['status']
        match value:
            case TrackingStatus.IN_PROGRESS.value:
                return TrackingStatus.IN_PROGRESS
            case TrackingStatus.COMPLETED.value:
                return TrackingStatus.COMPLETED
            case TrackingStatus.ALREADY.value:
                return TrackingStatus.ALREADY
            case TrackingStatus.NOT_FOUND.value:
                return TrackingStatus.NOT_FOUND
            case _:
                raise ValueError(f"Unexpected value: {value}")


class CommandResult(Protocol):
    """Base class for server response"""

    def to_dict(self) -> dict[str, Any]:
        pass

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'CommandResult':
        pass


class TrackingResult(CommandResult):
    def __init__(self, status: TrackingStatus, file_path: str) -> None:
        self.status: TrackingStatus = status
        self.file_path: str = file_path

    def to_dict(self) -> dict[str, Any]:
        return {
            'status': self.status.value,
            'file_path': self.file_path,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'TrackingResult':
        return TrackingResult(TrackingStatus.parse(data), data['file_path'])


class TrackingResults(CommandResult):
    def __init__(self, results: list[TrackingResult]) -> None:
        self.results: list[TrackingResult] = results

    def __iter__(self):
        return iter(self.results)

    def to_dict(self) -> dict[str, Any]:
        return {
            'results': list(map(lambda result: result.to_dict(), self.results))
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'TrackingResults':
        return TrackingResults(list(map(lambda result: TrackingResult.from_dict(result), data['results'])))


class ListTrackedResult(CommandResult):
    def __init__(self, file_paths: list[str]) -> None:
        self.file_paths: list[str] = file_paths

    def to_dict(self) -> dict[str, Any]:
        return {
            'file_paths': self.file_paths
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'ListTrackedResult':
        return ListTrackedResult(data['file_paths'])


class PingResult(CommandResult):
    def __init__(self, status_info: str) -> None:
        self.status_info: str = status_info

    def to_dict(self) -> dict[str, Any]:
        return {
            'status': self.status_info
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'PingResult':
        return PingResult(data['status'])


def parse_result(cmd: CommandType, data: dict[str, Any]) -> 'CommandResult':
    match cmd:
        case CommandType.ADD | CommandType.REMOVE:
            return TrackingResults.from_dict(data)
        case CommandType.LIST:
            return ListTrackedResult.from_dict(data)
        case CommandType.PING:
            return PingResult.from_dict(data)
        case _:
            raise ValueError()
