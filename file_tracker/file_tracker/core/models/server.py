import argparse
from dataclasses import dataclass, fields
from .base import DictJsonData, JsonSerializable


@dataclass
class ServerConfiguration(JsonSerializable):
    # from argparse
    use_unix_optimization: bool
    release_version: bool

    # set while working
    pid: int | None
    host_name: str | None
    host_port: int | None

    @staticmethod
    def parse(parser: argparse.ArgumentParser) -> 'ServerConfiguration':
        args = parser.parse_args()
        return ServerConfiguration(
            use_unix_optimization=args.unix_optimization,
            release_version=args.release,
            pid=None, host_name=None, host_port=None
        )

    def set_dynamic(self, pid: int, host_name: str, host_port: int) -> None:
        self.pid = pid
        if not self.use_unix_optimization:
            self.host_name = host_name
            self.host_port = host_port

    def to_json_data(self) -> DictJsonData:
        json_data = {}
        for field in fields(self):
            value = getattr(self, field.name)
            json_data[field.name] = value

        return json_data

    @staticmethod
    def from_json_data(json_data: DictJsonData) -> 'ServerConfiguration':
        kwargs = {}
        for field in fields(ServerConfiguration):
            value = json_data.get(field.name)
            kwargs[field.name] = value

        return ServerConfiguration(**kwargs)
