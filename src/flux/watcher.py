import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Callable

from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer


class IFileSystemWatcher(ABC):
    @abstractmethod
    def start(self) -> None:
        """Begin watching filesystem events."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop watching and clean up resources."""
        pass


class WatchdogWatcher(IFileSystemWatcher):
    def __init__(
        self,
        watch_paths: List[Path],
        include_patterns: List[str],
        ignore_patterns: List[str],
        on_event: Callable[[FileSystemEvent], None],
    ):
        """
        :param watch_paths:       directories or files to observe
        :param include_patterns:  glob patterns to include, e.g. ["*.py", "*.html"]
        :param ignore_patterns:   glob patterns to ignore, e.g. ["node_modules/*", "*.tmp"]
        :param on_event:          callback for any matching FileSystemEvent
        """
        self._observer = Observer()

        handler = PatternMatchingEventHandler(
            patterns=include_patterns,
            ignore_patterns=ignore_patterns,
            ignore_directories=True,
            case_sensitive=False,
        )
        # forward all matched events
        handler.on_created  = on_event
        handler.on_modified = on_event
        handler.on_moved    = on_event
        handler.on_deleted  = on_event

        for path in watch_paths:
            self._observer.schedule(handler, str(path), recursive=True)

    def start(self) -> None:
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()


class FileWatcherService:
    """
    Runs an IFileSystemWatcher on its own thread and
    forwards each event into an asyncio.Queue.
    """
    def __init__(self, watcher: IFileSystemWatcher, raw_q: asyncio.Queue):
        self._watcher = watcher
        self._raw_q   = raw_q

    async def run(self):
        self._watcher.start()
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self._watcher.stop()
            raise
