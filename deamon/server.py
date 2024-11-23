from deamon.base import CommandType, ResponseFormatter
from tracker import DirectoryTrackerManager
import asyncio


async def handle_client(reader, writer, file_observer: DirectoryTrackerManager, shutdown_event: asyncio.Event) -> None:
    addr = writer.get_extra_info("peername")
    print(f"Connected: {addr}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break

            request_part = data.decode().strip().split(" ", 1)
            cmd = CommandType(request_part[0])
            argument = request_part[1] if len(request_part) > 1 else None

            result, response = None, None
            if cmd == CommandType.ADD and argument:
                result = file_observer.start_watching(argument)
            elif cmd == CommandType.REMOVE and argument:
                result = file_observer.stop_watching(argument)
            elif cmd == CommandType.LIST:
                result = file_observer.list_watched_files()
            elif cmd == CommandType.EXIT:
                response = "Stopping server"
                shutdown_event.set()
            else:
                response = f"Wrong command: {cmd.value} {argument}"

            if not response:
                response = ResponseFormatter.make(cmd, result)

            writer.write((response + "\n").encode("utf-8"))
            await writer.drain()
    except asyncio.CancelledError:
        pass
    finally:
        print(f"Disconnected: {addr}")
        writer.close()
        await writer.wait_closed()


HOST_NAME = "localhost"
PORT = 9998


async def main() -> None:
    file_observer = DirectoryTrackerManager()
    shutdown_event = asyncio.Event()
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, file_observer, shutdown_event), HOST_NAME, PORT
    )
    print(f"Work on {HOST_NAME} {PORT} port")

    async with server:
        await shutdown_event.wait()
        print("Stopping server")
        file_observer.stop_all()


if __name__ == "__main__":
    asyncio.run(main())
