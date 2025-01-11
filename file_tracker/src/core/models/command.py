from enum import Enum
from typing import Protocol
from .base import DictJsonData, JsonSerializable


class CommandType(Enum):
    ADD = 'add'
    REMOVE = 'remove'
    LIST = 'list'
    PING = 'ping'

    @staticmethod
    def parse(json_data: DictJsonData) -> 'CommandType':
        value = json_data['command']

        for member in CommandType:
            if member.value == value:
                return member


class Command(JsonSerializable, Protocol):
    @property
    def type(self) -> CommandType:
        pass

    def to_json_data(self) -> DictJsonData:
        pass

    @staticmethod
    def from_json_data(json_data: DictJsonData) -> 'Command':
        pass


class AddCommand(Command):
    cmd_type = CommandType.ADD

    @property
    def type(self) -> CommandType:
        return self.cmd_type

    def __init__(self, file_paths: list[str]) -> None:
        self.file_paths: list[str] = file_paths

    def to_json_data(self) -> DictJsonData:
        return {
            'command': self.type.value,
            'file_paths': self.file_paths
        }

    @staticmethod
    def from_json_data(json_data: DictJsonData) -> 'AddCommand':
        cmd_type = CommandType.parse(json_data)
        if cmd_type != AddCommand.cmd_type:
            raise ValueError(cmd_type)
        return AddCommand(json_data['file_paths'])


class RemoveCommand(Command):
    cmd_type = CommandType.REMOVE

    @property
    def type(self) -> CommandType:
        return self.cmd_type

    def __init__(self, file_paths: list[str]) -> None:
        self.file_paths: list[str] = file_paths

    def to_json_data(self) -> DictJsonData:
        return {
            'command': self.type.value,
            'file_paths': self.file_paths
        }

    @staticmethod
    def from_json_data(json_data: DictJsonData) -> 'RemoveCommand':
        cmd_type = CommandType.parse(json_data)
        if cmd_type != RemoveCommand.cmd_type:
            raise ValueError(cmd_type)
        return RemoveCommand(json_data['file_paths'])


class SimpleCommand(Command):
    def __init__(self, cmd_type: CommandType):
        self.cmd_type = cmd_type

    @property
    def type(self) -> CommandType:
        return self.cmd_type

    def to_json_data(self) -> DictJsonData:
        return {
            'command': self.type.value,
        }

    @staticmethod
    def from_json_data(json_data: DictJsonData) -> 'SimpleCommand':
        return SimpleCommand(CommandType.parse(json_data))


def parse_command(json_data: DictJsonData) -> 'Command':
    cmd_type = CommandType.parse(json_data)
    match cmd_type:
        case CommandType.ADD:
            return AddCommand.from_json_data(json_data)
        case CommandType.REMOVE:
            return RemoveCommand.from_json_data(json_data)
        case CommandType.LIST | CommandType.PING:
            return SimpleCommand.from_json_data(json_data)
        case _:
            raise ValueError()
