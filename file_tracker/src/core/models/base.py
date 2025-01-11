from typing import Any, Protocol

DictJsonData = dict[str, Any]
ListJsonData = list[DictJsonData]
JsonData = DictJsonData | ListJsonData


class JsonSerializable(Protocol):
    def to_json_data(self) -> JsonData:
        pass

    @staticmethod
    def from_json_data(json_data: JsonData) -> 'JsonSerializable':
        pass
