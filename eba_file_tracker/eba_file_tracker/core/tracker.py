import os
import socket
import logging
import requests
from datetime import datetime, timezone
from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent, DirDeletedEvent, \
    FileDeletedEvent
from watchdog.observers import Observer
from .models.tracker import File, FileMetadata
from .models.result import CommandResultType, TrackingStatus, TrackingInfoResult, TrackedInfoResult, \
    ListTrackedInfoResult, InfoResult


def format_timestamp_to_iso8601(timestamp) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def send_metadata_to_server(metadata: FileMetadata) -> None:
    try:
        if not metadata:
            raise ValueError("Empty metadata")
        response = requests.post("http://127.0.0.1:8000/client/add_event", json=metadata.to_json_data())
        if response.status_code == 200:
            logging.info(f"Metadata has been sent successfully: {metadata.file_path}")
        else:
            logging.error(f"Error while sending metadata: {response.status_code}")
    except Exception as e:
        logging.error(f"Couldn't send metadata: {e}")


class DirectoryEventHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.files: dict[str, File] = dict()

    def add_file(self, file: File) -> bool:
        if file.file_path in self.files:
            return False

        self.files[file.file_path] = file
        return True

    def remove_file(self, file_path: str) -> bool:
        if file_path not in self.files:
            return False

        self.files.pop(file_path)
        return True

    def get_metadata(self, file_path: str) -> FileMetadata | None:
        if file_path not in self.files:
            return None

        stats = os.stat(file_path)
        return FileMetadata(
            hostname=socket.gethostname(),
            file_path=file_path,
            dataset_general_info_id=self.files[file_path].file_id,
            age=format_timestamp_to_iso8601(stats.st_ctime),
            access_rights=oct(stats.st_mode)[-3:],
            last_access_date=format_timestamp_to_iso8601(stats.st_atime),
            last_modification_date=format_timestamp_to_iso8601(stats.st_mtime),
            size=stats.st_size,
        )

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        if event.src_path in self.files:
            logging.info(f"File modified: {event.src_path}")
            metadata = self.get_metadata(event.src_path)
            send_metadata_to_server(metadata)

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        if event.src_path in self.files:
            if self.remove_file(event.src_path):
                logging.info(f"File deleted: {event.src_path}")


class SingleDirectoryTracker:
    def __init__(self, dir_path: str) -> None:
        super().__init__()
        self._handler = DirectoryEventHandler()
        self._observer = Observer()

        self._observer.schedule(self._handler, dir_path, recursive=False)
        self._observer.start()

    def add_file(self, file: File) -> bool:
        return self._handler.add_file(file)

    def remove_file(self, file_path: str) -> bool:
        return self._handler.remove_file(file_path)

    def get_file_info(self, file_path: str) -> FileMetadata | None:
        return self._handler.get_metadata(file_path)

    def empty(self) -> bool:
        return len(self._handler.files) == 0

    def list(self) -> list[str]:
        return list(self._handler.files.keys())

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()


class DirectoryTrackerManager:
    def __init__(self):
        self.tracker: dict[str, SingleDirectoryTracker] = dict()

    def start_watching(self, file: File) -> TrackingInfoResult:
        if not os.path.exists(file.file_path):
            return TrackingInfoResult(CommandResultType.ADD, TrackingStatus.NOT_FOUND, file.file_path)

        dir_path = os.path.dirname(file.file_path)
        if dir_path not in self.tracker:
            self.tracker[dir_path] = SingleDirectoryTracker(dir_path)

        if self.tracker[dir_path].add_file(file):
            return TrackingInfoResult(CommandResultType.ADD, TrackingStatus.IN_PROGRESS, file.file_path)
        else:
            return TrackingInfoResult(CommandResultType.ADD, TrackingStatus.ALREADY, file.file_path)

    def stop_watching(self, file_path: str) -> TrackingInfoResult:
        if not os.path.exists(file_path):
            return TrackingInfoResult(CommandResultType.REMOVE, TrackingStatus.NOT_FOUND, file_path)

        dir_path = os.path.dirname(file_path)
        if dir_path not in self.tracker:
            return TrackingInfoResult(CommandResultType.REMOVE, TrackingStatus.ALREADY, file_path)

        tracker = self.tracker[dir_path]
        is_success = tracker.remove_file(file_path)

        if tracker.empty():
            self._remove_tracker(dir_path)

        return TrackingInfoResult(CommandResultType.REMOVE, TrackingStatus.COMPLETED, file_path) if is_success \
            else TrackingInfoResult(CommandResultType.REMOVE, TrackingStatus.ALREADY, file_path)

    def get_file_info(self, file_path: str) -> InfoResult:
        if not os.path.exists(file_path):
            return InfoResult(None)

        dir_path = os.path.dirname(file_path)
        if dir_path not in self.tracker:
            return InfoResult(None)

        tracker = self.tracker[dir_path]
        return InfoResult(tracker.get_file_info(file_path))

    def list_watched_files(self) -> ListTrackedInfoResult:
        watched_files: list[TrackedInfoResult] = []
        for tracker in self.tracker.values():
            watched_files.extend(
                map(
                    lambda tracker_file: TrackedInfoResult(tracker_file),
                    tracker.list()
                )
            )
        return ListTrackedInfoResult(watched_files)

    def stop_all_watching(self) -> None:
        for dir_path in list(self.tracker.keys()):
            self._remove_tracker(dir_path)

    def _remove_tracker(self, dir_path: str) -> None:
        tracker = self.tracker.pop(dir_path)
        tracker.stop()
        del tracker
