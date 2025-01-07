import asyncio
import json
from typing import Any


async def write_json(writer: asyncio.StreamWriter, data: dict[str, Any]) -> None:
    json_data = json.dumps(data)
    writer.write(json_data.encode("utf-8"))
    await writer.drain()
    writer.write_eof()


async def read_json(reader: asyncio.StreamReader) -> dict[str, Any]:
    data = b""
    while not reader.at_eof():
        chunk = await reader.read(1024)
        data += chunk
    return json.loads(data.decode("utf-8"))
