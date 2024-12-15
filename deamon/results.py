from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class TrackingStatus(Enum):
    IN_PROGRESS = auto()
    COMPLETED = auto()
    ALREADY = auto()
    NOT_FOUND = auto()


@dataclass
class TrackingResult:
    status: TrackingStatus
    file_path: str | None


@dataclass
class ListTrackedResult:
    list: List[str]
