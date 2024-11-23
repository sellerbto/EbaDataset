from watcher import FileObserver
import asyncio


async def handle_client(reader, writer, file_observer: FileObserver) -> None:
    addr = writer.get_extra_info("peername")
    print(f"Клиент подключён: {addr}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break

            command = data.decode().strip().split(" ", 1)
            action = command[0]
            argument = command[1] if len(command) > 1 else None

            if action == "add" and argument:
                response = file_observer.start_watching(argument)
            elif action == "remove" and argument:
                response = file_observer.stop_watching(argument)
            elif action == "list":
                response = file_observer.list_watched_files()
            elif action == "exit":
                response = "Сервер будет остановлен."
                await writer.drain()
                asyncio.get_event_loop().stop()
            else:
                response = "Неизвестная команда."

            writer.write((response + "\n").encode("utf-8"))
            await writer.drain()

    except asyncio.CancelledError:
        pass
    finally:
        print(f"Клиент отключён: {addr}")
        writer.close()
        await writer.wait_closed()


async def main():
    file_observer = FileObserver()
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, file_observer), "localhost", 9999
    )
    print("Сервер запущен на порту 9999")

    try:
        async with server:
            await server.serve_forever()
    finally:
        file_observer.stop_all()


if __name__ == "__main__":
    asyncio.run(main())
