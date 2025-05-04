import asyncio
from typing import List, Optional
from flux.debouncer import ReloadSignal
from asyncio.subprocess import Process

async def process_mgr(
    reload_q: asyncio.Queue[ReloadSignal],
    ui_q: Optional[asyncio.Queue],
    cmd: List[str],
) -> None:
    """
    Launch the subprocess, forward its stdout/stderr to this process's stdout/stderr,
    and restart it on each ReloadSignal.
    """
    proc: Optional[Process] = None

    async def start_process():
        nonlocal proc
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        print(f"\n[flux] ▶ Started PID={proc.pid}\n", flush=True)
        # stream stdout/stderr
        async def _stream(reader, is_err=False):
            while True:
                line = await reader.readline()
                if not line:
                    break
                text = line.decode(errors="replace").rstrip("\n")
                if is_err:
                    print(f"[flux][stderr] {text}", flush=True)
                else:
                    print(f"[flux][stdout] {text}", flush=True)

        asyncio.create_task(_stream(proc.stdout, is_err=False))
        asyncio.create_task(_stream(proc.stderr, is_err=True))

    # initial start
    await start_process()

    try:
        while True:
            # wait for debouncer
            await reload_q.get()

            if proc and proc.returncode is None:
                print(f"\n[flux] ⏹ Stopping PID={proc.pid}", flush=True)
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.wait()
                print(f"[flux] ⚡ Restarting (exit={proc.returncode})\n", flush=True)

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
