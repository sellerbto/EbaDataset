from datetime import datetime
from dataclasses import dataclass, fields
from .base import JsonSerializable, DictJsonData


@dataclass
class File(JsonSerializable):
    file_path: str
    file_id: int


@dataclass
class FileMetadata(JsonSerializable):
    hostname: str
    file_path: str
    file_id: int
    age: datetime
    access_rights: str
    last_access_date: datetime
    last_modification_date: datetime
    size: int

    def to_json_data(self) -> DictJsonData:
        json_data = {}
        for field in fields(self):
            value = getattr(self, field.name)
            json_data[field.name] = value

        return json_data

    @staticmethod
    def is_correct(json_data: DictJsonData) -> bool:
        for field in fields(FileMetadata):
            if field.name not in json_data:
                return False

        return True

    @staticmethod
    def from_json_data(json_data: DictJsonData) -> 'FileMetadata':
        kwargs = {}
        for field in fields(FileMetadata):
            value = json_data.get(field.name)
            kwargs[field.name] = value

        return FileMetadata(**kwargs)
