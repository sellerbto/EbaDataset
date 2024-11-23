from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent, DirDeletedEvent, \
    FileDeletedEvent
from typing import Set, Dict, List
import time
import os


def get_metadata(path):
    stats = os.stat(path)
    return {
        "Размер": stats.st_size,
        "Возраст": time.time() - stats.st_ctime,
        "Права доступа": oct(stats.st_mode)[-3:],
        "Дата последнего обращения": time.ctime(stats.st_ctime),
        "Дата последнего изменения": time.ctime(stats.st_mtime),
    }


class DirectoryHandler(FileSystemEventHandler):
    def __init__(self, dir_path: str) -> None:
        super().__init__()
        self.file_paths: Set[str] = set()
        self.observer = Observer()
        self.observer.schedule(self, dir_path, recursive=False)
        self.observer.start()

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
            print(f"Файл изменен: {event.src_path}")
            print(get_metadata(event.src_path))

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        if event.src_path == self.file_paths:
            print(f"Файл удален: {event.src_path}")
            self.remove_file(event.src_path)


class FileObserver:
    def __init__(self):
        self.handlers: Dict[str, DirectoryHandler] = dict()

    def start_watching(self, file_path: str) -> None:
        if not os.path.exists(file_path):
            print(f"Файл не найден: {file_path}")

        dir_path = os.path.dirname(file_path)
        if dir_path not in self.handlers:
            self.handlers[dir_path] = DirectoryHandler(dir_path)

        if self.handlers[dir_path].add_file(file_path):
            print(f"Начато наблюдение за: {file_path}")
        else:
            print(f"Файл уже отслеживается: {file_path}")

    def stop_watching(self, file_path: str) -> None:
        dir_path = os.path.dirname(file_path)
        if dir_path not in self.handlers:
            print(f"Файл не находится под наблюдением: {file_path}")

        handler = self.handlers[dir_path]
        if handler.remove_file(file_path):
            print(f"Файл не отслеживался: {file_path}")
        else:
            print(f"Наблюдение за {file_path} остановлено")

        if len(handler.file_paths) == 0:
            self._remove_handler(dir_path)

    def list_watched_files(self) -> List[str]:
        print("Отслеживаемые файлы:")
        for handler in self.handlers.values():
            for file_path in handler.file_paths:
                print(f" - {file_path}")

    def stop_all(self) -> None:
        for dir_path in self.handlers.keys():
            self._remove_handler(dir_path)

    def _remove_handler(self, dir_path: str) -> None:
        handler = self.handlers.pop(dir_path)
        handler.observer.stop()
        handler.observer.join()


def main():
    fileObserver = FileObserver()

    try:
        while True:
            print("\nМеню:")
            print("1. Добавить файл для отслеживания")
            print("2. Удалить файл из отслеживания")
            print("3. Список отслеживаемых файлов")
            print("4. Выйти")
            choice = input("Выберите действие: ")

            if choice == "1":
                file_path = input("Введите полный путь к файлу: ")
                fileObserver.start_watching(file_path)
            elif choice == "2":
                file_path = input("Введите полный путь к файлу: ")
                fileObserver.stop_watching(file_path)
            elif choice == "3":
                fileObserver.list_watched_files()
            elif choice == "4":
                break
            else:
                print("Неверный выбор. Попробуйте снова.")
    except KeyboardInterrupt:
        print("\nЗавершаем наблюдение...")
    finally:
        fileObserver.stop_all()


if __name__ == "__main__":
    main()
