# src/flux/app.py

import asyncio
from pathlib import Path
from typing import List

from flux.config import Settings
from flux.watcher import WatchdogWatcher, FileWatcherService


async def run_pipeline(settings: Settings):
    """
    Build and run the async pipeline:
      Watcher → Debouncer → ProcessMgr → Renderer
    """
    loop = asyncio.get_event_loop()

    raw_q = asyncio.Queue()

    def _on_event(event):
        loop.call_soon_threadsafe(raw_q.put_nowait, event)

    include_patterns = (
        [f"*.{ext.lstrip('.')}" for ext in settings.exts]
        if settings.exts else ["*"]
    )
    ignore_patterns = [str(p) for p in settings.ignore_paths]

    watcher_impl = WatchdogWatcher(
        watch_paths      = settings.watch_paths,
        include_patterns = include_patterns,
        ignore_patterns  = ignore_patterns,
        on_event         = _on_event,
    )
    watcher_service = FileWatcherService(watcher_impl, raw_q)

    tasks: List[asyncio.Task] = [
        asyncio.create_task(watcher_service.run()),
    ]

    try:
        await asyncio.gather(*tasks)
    except (asyncio.CancelledError, KeyboardInterrupt):
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
