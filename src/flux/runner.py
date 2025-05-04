# src/flux/runner.py

import asyncio
from typing import List, Tuple, Union

from asyncio.subprocess import Process, PIPE

from flux.debouncer import ReloadSignal

# Type alias for UI events
UIEvent = Tuple[str, Union[int, str]]


async def process_mgr(
    reload_q: asyncio.Queue[ReloadSignal],
    ui_q: asyncio.Queue[UIEvent],
    cmd: List[str],
) -> None:
    """
    Launch a subprocess for `cmd`, forward its stdout/stderr into `ui_q`,
    and restart it whenever a ReloadSignal arrives on `reload_q`.
    """
    proc: Process | None = None

    async def start_process():
        nonlocal proc
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        ui_q.put_nowait(("proc_started", proc.pid))

        asyncio.create_task(read_stream(proc.stdout, "stdout"))
        asyncio.create_task(read_stream(proc.stderr, "stderr"))

    async def read_stream(stream: asyncio.StreamReader, label: str):
        """Read lines from the given stream and push (label, text) into ui_q."""
        assert stream is not None
        while True:
            line = await stream.readline()
            if not line:
                break
            ui_q.put_nowait((label, line.decode(errors="replace")))

    await start_process()

    try:
        while True:
            await reload_q.get()

            if proc and proc.returncode is None:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.wait()

                ui_q.put_nowait(("proc_exited", proc.returncode))

            await start_process()

    except asyncio.CancelledError:
        if proc and proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
        raise
