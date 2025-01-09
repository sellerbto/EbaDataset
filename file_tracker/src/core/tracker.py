import os
import socket
from datetime import datetime, timezone
from typing import Any

import requests
from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent, DirDeletedEvent, \
    FileDeletedEvent
from watchdog.observers import Observer
from .model import TrackingResult, TrackingStatus


def format_timestamp_to_iso8601(timestamp) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def get_metadata(file_path: str) -> dict[str, Any]:
    stats = os.stat(file_path)
    return {
        "hostname": socket.gethostname(),
        "file_path": file_path,
        "dataset_name": "dummy",
        "age": format_timestamp_to_iso8601(stats.st_ctime),
        "access_rights": oct(stats.st_mode)[-3:],
        "last_access_date": format_timestamp_to_iso8601(stats.st_atime),
        "last_modification_date": format_timestamp_to_iso8601(stats.st_mtime),
        "size": stats.st_size,
    }


def send_metadata_to_server(metadata: dict[str, Any]) -> None:
    try:
        response = requests.post("http://127.0.0.1:8000/client/add_event", json=metadata)
        if response.status_code == 200:
            print(f"Метаданные успешно отправлены: {metadata['dataset_name']}")
        else:
            print(f"Ошибка отправки метаданных: {response.status_code}")
    except Exception as e:
        print(f"Не удалось отправить метаданные: {e}")


class DirectoryEventHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.file_paths: set[str] = set()

    def add_file(self, file_path: str) -> bool:
        if file_path in self.file_paths:
            return False

        self.file_paths.add(file_path)
        return True

    def remove_file(self, file_path: str) -> bool:
        if file_path not in self.file_paths:
            return False

        self.file_paths.remove(file_path)
        return True

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        if event.src_path in self.file_paths:
            print(f"File modified: {event.src_path}")
            metadata = get_metadata(event.src_path)
            print(metadata)
            send_metadata_to_server(metadata)

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        if event.src_path in self.file_paths:
            if self.remove_file(event.src_path):
                print(f"File deleted: {event.src_path}")


class SingleDirectoryTracker:
    def __init__(self, dir_path: str) -> None:
        super().__init__()
        self._handler = DirectoryEventHandler()
        self._observer = Observer()

        self._observer.schedule(self._handler, dir_path, recursive=False)
        self._observer.start()

    def add_file(self, file_path: str) -> bool:
        return self._handler.add_file(file_path)

    def remove_file(self, file_path: str) -> bool:
        return self._handler.remove_file(file_path)

    def empty(self) -> bool:
        return len(self._handler.file_paths) == 0

    def list(self) -> list[str]:
        return list(self._handler.file_paths)

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()


class DirectoryTrackerManager:
    def __init__(self):
        self.tracker: dict[str, SingleDirectoryTracker] = dict()

    def start_watching(self, file_path: str) -> TrackingResult:
        if not os.path.exists(file_path):
            return TrackingResult(TrackingStatus.NOT_FOUND, file_path)

        dir_path = os.path.dirname(file_path)
        if dir_path not in self.tracker:
            self.tracker[dir_path] = SingleDirectoryTracker(dir_path)

        if self.tracker[dir_path].add_file(file_path):
            return TrackingResult(TrackingStatus.IN_PROGRESS, file_path)
        else:
            return TrackingResult(TrackingStatus.ALREADY, file_path)

    def stop_watching(self, file_path: str) -> TrackingResult:
        if not os.path.exists(file_path):
            return TrackingResult(TrackingStatus.NOT_FOUND, file_path)

        dir_path = os.path.dirname(file_path)
        if dir_path not in self.tracker:
            return TrackingResult(TrackingStatus.ALREADY, file_path)

        tracker = self.tracker[dir_path]
        is_success = tracker.remove_file(file_path)

        if tracker.empty():
            self._remove_tracker(dir_path)

        return TrackingResult(TrackingStatus.ALREADY, file_path) if is_success \
            else TrackingResult(TrackingStatus.COMPLETED, file_path)

    def list_watched_files(self) -> list[str]:
        watched_files = []
        for tracker in self.tracker.values():
            watched_files.extend(tracker.list())
        return watched_files

    def stop_all_watching(self) -> None:
        for dir_path in self.tracker.keys():
            self._remove_tracker(dir_path)

    def _remove_tracker(self, dir_path: str) -> None:
        tracker = self.tracker.pop(dir_path)
        tracker.stop()
        del tracker
