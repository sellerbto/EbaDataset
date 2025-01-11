import json
import asyncio
from ..models.base import JsonData


async def read_json(reader: asyncio.StreamReader) -> JsonData:
    data = b""
    while not reader.at_eof():
        chunk = await reader.read(1024)
        data += chunk
    return json.loads(data.decode("utf-8"))


async def write_json(writer: asyncio.StreamWriter, json_data: JsonData) -> None:
    json_data = json.dumps(json_data)
    writer.write(json_data.encode("utf-8"))
    await writer.drain()
    writer.write_eof()


def read_json_from_file(file_path: str) -> JsonData:
    with open(file_path, "r") as file:
        json_data = json.load(file)
        return json_data


def write_json_to_file(file_path: str, json_data: JsonData) -> None:
    with open(file_path, "w") as file:
        json.dump(json_data, file, indent=4)
