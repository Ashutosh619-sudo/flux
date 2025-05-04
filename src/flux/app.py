# src/flux/app.py

import asyncio
from flux.config import Settings
from flux.watcher import WatchdogWatcher, FileWatcherService
from flux.debouncer import debouncer
from flux.runner import process_mgr


async def run_pipeline(settings: Settings):
    """
    Watch → Debounce → Restart, but forward all child I/O directly to stdout.
    """
    loop = asyncio.get_event_loop()

    raw_q = asyncio.Queue()
    reload_q = asyncio.Queue()

    def _on_event(ev):
        loop.call_soon_threadsafe(raw_q.put_nowait, ev)

    include = [f"*.{ext.lstrip('.')}" for ext in settings.exts] or ["*"]
    ignore = [str(p) for p in settings.ignore_paths]

    watcher = WatchdogWatcher(settings.watch_paths, include, ignore, _on_event)
    watcher_svc = FileWatcherService(watcher, raw_q)

    tasks = [
        asyncio.create_task(watcher_svc.run()),
        asyncio.create_task(debouncer(raw_q, reload_q, settings.debounce_ms)),
        asyncio.create_task(process_mgr(reload_q, None, settings.cmd)),
    ]

    try:
        await asyncio.gather(*tasks)
    except (KeyboardInterrupt, asyncio.CancelledError):
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
