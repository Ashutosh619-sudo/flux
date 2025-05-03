import asyncio
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ReloadSignal:
    """Sentinel to tell the ProcessMgr to restart."""
    pass

async def debouncer(
    raw_q: asyncio.Queue[Any],
    reload_q: asyncio.Queue[ReloadSignal],
    debounce_ms: int
) -> None:
    """
    Consume filesystem events from raw_q, coalesce bursts over debounce_ms,
    and emit a single ReloadSignal into reload_q per burst.

    :param raw_q:       incoming raw FileSystemEvent objects
    :param reload_q:    queue to send ReloadSignal() into
    :param debounce_ms: debounce window in milliseconds
    """
    while True:
        _ = await raw_q.get()

        try:
            while True:
                await asyncio.wait_for(
                    raw_q.get(),
                    timeout=debounce_ms / 1000.0
                )
        except asyncio.TimeoutError:
            pass

        reload_q.put_nowait(ReloadSignal())
