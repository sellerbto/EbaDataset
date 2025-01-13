from enum import Enum, auto
from typing import Protocol
from .base import DictJsonData, ListJsonData, JsonData, JsonSerializable
from .command import CommandType
from .tracker import FileMetadata
from .server import ServerConfiguration


class CommandResultType(Enum):
    ADD = 'add'
    REMOVE = 'remove'
    LIST = 'list'
    PING = 'ping'

    @staticmethod
    def parse(json_data: DictJsonData) -> 'CommandResultType':
        value = json_data['command_result']

        for member in CommandResultType:
            if member.value == value:
                return member


class CommandResult(JsonSerializable, Protocol):
    def to_json_data(self) -> JsonData:
        pass

    @staticmethod
    def from_json_data(json_data: JsonData) -> 'CommandResult':
        pass


class TrackingStatus(Enum):
    IN_PROGRESS = auto()
    COMPLETED = auto()
    ALREADY = auto()
    NOT_FOUND = auto()

    @staticmethod
    def parse(json_data: DictJsonData) -> 'TrackingStatus':
        value = json_data['status']

        for member in TrackingStatus:
            if member.value == value:
                return member


class TrackingInfoResult(CommandResult):
    def __init__(
        self,
        cmd_type: CommandResultType,
        status: TrackingStatus,
        file_path: str
    ) -> None:
        self.type = cmd_type
        self.status: TrackingStatus = status
        self.file_path: str = file_path

    def to_json_data(self) -> DictJsonData:
        return {
            'command_result': self.type.value,
            'status': self.status.value,
            'file_path': self.file_path,
        }

    @staticmethod
    def from_json_data(json_data: DictJsonData) -> 'TrackingInfoResult':
        cmd_type = CommandResultType.parse(json_data)
        if cmd_type not in [CommandResultType.ADD, CommandResultType.REMOVE]:
            raise ValueError(cmd_type)
        return TrackingInfoResult(cmd_type, TrackingStatus.parse(json_data), json_data['file_path'])


class ListTrackingInfoResult(CommandResult):
    def __init__(self, results: list[TrackingInfoResult]) -> None:
        self.results: list[TrackingInfoResult] = results

    def __iter__(self):
        return iter(self.results)

    def to_json_data(self) -> ListJsonData:
        return list(map(lambda result: result.to_json_data(), self.results))

    @staticmethod
    def from_json_data(json_data: ListJsonData) -> 'ListTrackingInfoResult':
        return ListTrackingInfoResult(list(map(lambda result: TrackingInfoResult.from_json_data(result), json_data)))


class TrackedInfoResult(CommandResult):
    type = CommandResultType.LIST

    def __init__(self, meta: FileMetadata) -> None:
        self.file_path: str = meta.file_path

    def to_json_data(self) -> DictJsonData:
        return {
            'command_result': self.type.value,
            'file_path': self.file_path,
        }

    @staticmethod
    def from_json_data(json_data: DictJsonData) -> 'TrackedInfoResult':
        cmd_type = CommandResultType.parse(json_data)
        if cmd_type != TrackedInfoResult.type:
            raise ValueError(cmd_type)
        return TrackedInfoResult(FileMetadata.from_json_data(json_data))


class ListTrackedInfoResult(CommandResult):
    def __init__(self, results: list[TrackedInfoResult]) -> None:
        self.results = results

    def __iter__(self):
        return iter(self.results)

    def to_json_data(self) -> ListJsonData:
        return list(map(lambda result: result.to_json_data(), self.results))

    @staticmethod
    def from_json_data(json_data: ListJsonData) -> 'ListTrackedInfoResult':
        return ListTrackedInfoResult(list(map(lambda result: TrackedInfoResult.from_json_data(result), json_data)))


class PingResult(CommandResult):
    def __init__(self, configuration: ServerConfiguration) -> None:
        self.type = CommandResultType.PING
        self.configuration = configuration

    def to_json_data(self) -> DictJsonData:
        json_data = self.configuration.to_json_data()
        json_data['command_result'] = self.type.value
        return json_data

    @staticmethod
    def from_json_data(json_data: DictJsonData) -> 'PingResult':
        cmd_type = CommandResultType.parse(json_data)
        if cmd_type != CommandResultType.PING:
            raise ValueError(cmd_type)
        return PingResult(ServerConfiguration.from_json_data(json_data))


def parse_result(cmd_type: CommandType, json_data: JsonData) -> 'CommandResult':
    match cmd_type:
        case CommandType.ADD | CommandType.REMOVE:
            return ListTrackingInfoResult.from_json_data(json_data)
        case CommandType.LIST:
            return ListTrackedInfoResult.from_json_data(json_data)
        case CommandType.PING:
            return PingResult.from_json_data(json_data)
        case _:
            raise ValueError()
