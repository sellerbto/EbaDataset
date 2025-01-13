from .core.models.server import ServerConfiguration
from .core.models.result import TrackingStatus, CommandResultType, ListTrackingInfoResult, ListTrackedInfoResult


class ResponseFormatter:
    @staticmethod
    def make_from_configuration(configuration: ServerConfiguration) -> str:
        response = []
        json_data = configuration.to_json_data()
        for key in json_data.keys():
            if json_data[key] is not None:
                response.append(f"- {key}={json_data[key]}")

        return '\n'.join(response)

    @staticmethod
    def make_from_add(add_results: ListTrackingInfoResult) -> str:
        response = ["The result of adding files to tracking:"]
        for result in add_results:
            if result.type != CommandResultType.ADD:
                raise ValueError(result.type.value)
            match result.status:
                case TrackingStatus.IN_PROGRESS:
                    response.append(f"- file tracking started: {result.file_path}")
                case TrackingStatus.ALREADY:
                    response.append(f"- file is already being tracked: {result.file_path}")
                case TrackingStatus.NOT_FOUND:
                    response.append(f"- file not found: {result.file_path}")
                case _:
                    raise ValueError(result.status)

        return '\n'.join(response)

    @staticmethod
    def make_from_remove(remove_results: ListTrackingInfoResult) -> str:
        response = ["The result of remove files from tracking:"]
        for result in remove_results:
            if result.type != CommandResultType.REMOVE:
                raise ValueError(result.type.value)
            match result.status:
                case TrackingStatus.COMPLETED:
                    response.append(f"- file tracking stopped: {result.file_path}")
                case TrackingStatus.ALREADY:
                    response.append(f"- file is not tracked: {result.file_path}")
                case TrackingStatus.NOT_FOUND:
                    response.append(f"- file not found: {result.file_path}")
                case _:
                    raise ValueError(result.status)

        return '\n'.join(response)

    @staticmethod
    def make_from_list(list_results: ListTrackedInfoResult) -> str:
        response = ["List of tracked files:"]
        for result in list_results:
            if result.type != CommandResultType.LIST:
                raise ValueError(result.type.value)
            response.append(f"- {result.file_path}")

        return '\n'.join(response)

