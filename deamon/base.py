from enum import Enum

from results import TrackingResult, TrackingStatus, ListTrackedResult


class CommandType(Enum):
    ADD = "add"
    REMOVE = "remove"
    LIST = "list"
    EXIT = "exit"



class ResponseFormatter:
    @staticmethod
    def make(cmd: CommandType, result) -> str:
        if isinstance(result, TrackingResult):
            if cmd not in [CommandType.ADD, CommandType.REMOVE]:
                raise ValueError()

            match (result.status):
                case TrackingStatus.IN_PROGRESS:
                    if cmd != CommandType.ADD:
                        raise ValueError()
                    return f"File tracking started: {result.file_path}"
                case TrackingStatus.COMPLETED:
                    if cmd != CommandType.REMOVE:
                        raise ValueError()
                    return f"File tracking stopped: {result.file_path}"
                case TrackingStatus.ALREADY:
                    return f"File already tracked: {result.file_path}" if cmd == CommandType.ADD \
                        else f"File already under tracked: {result.file_path}"
                case TrackingStatus.NOT_FOUND:
                    return f"File not found: {result.file_path}"
        elif isinstance(result, ListTrackedResult):
            return '\n'.join(["Tracked files:"] + list(map(lambda file_path: "- " + file_path, result.list)))
        else:
            print(type(result))
            raise ValueError()
