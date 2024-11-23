import socket
from watchdog.observers import Observer
from main_server.app.schemas.requests import ClientRequest
from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent, DirDeletedEvent, \
    FileDeletedEvent
from deamon.base import TrackingResult, TrackingStatus, ListTrackedResult
from typing import Set, Dict, List
import time
import os


def get_metadata(file_path: str) -> ClientRequest:
    stats = os.stat(file_path)
    client_response = ClientRequest(
        hostname=socket.gethostname(),
        age=stats.st_ctime,
        access=oct(stats.st_mode)[-3:],
        last_access=time.ctime(stats.st_ctime),
        last_modified=time.ctime(stats.st_mtime),
    )
    return client_response


class DirectoryHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.file_paths: Set[str] = set()

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
            print(get_metadata(event.src_path))

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        if event.src_path in self.file_paths:
            if self.remove_file(event.src_path):
                print(f"File deleted: {event.src_path}")


class DirectoryTracker:
    def __init__(self, dir_path: str) -> None:
        super().__init__()
        self._handler = DirectoryHandler()
        self._observer = Observer()

        self._observer.schedule(self._handler, dir_path, recursive=False)
        self._observer.start()

    def add_file(self, file_path: str) -> bool:
        return self._handler.add_file(file_path)

    def remove_file(self, file_path: str) -> bool:
        return self._handler.remove_file(file_path)

    def empty(self) -> bool:
        return len(self._handler.file_paths) == 0

    def list(self) -> List[str]:
        return list(self._handler.file_paths)

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()


class DirectoryTrackerManager:
    def __init__(self):
        self.tracker: Dict[str, DirectoryTracker] = dict()

    def start_watching(self, file_path: str) -> TrackingResult:
        if not os.path.exists(file_path):
            return TrackingResult(TrackingStatus.NOT_FOUND, file_path)

        dir_path = os.path.dirname(file_path)
        if dir_path not in self.tracker:
            self.tracker[dir_path] = DirectoryTracker(dir_path)

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

    def list_watched_files(self) -> ListTrackedResult:
        tracked = ListTrackedResult([])
        for tracker in self.tracker.values():
            tracked.list.extend(tracker.list())
        return tracked

    def stop_all(self) -> None:
        for dir_path in self.tracker.keys():
            self._remove_tracker(dir_path)

    def _remove_tracker(self, dir_path: str) -> None:
        tracker = self.tracker.pop(dir_path)
        tracker.stop()
        del tracker
