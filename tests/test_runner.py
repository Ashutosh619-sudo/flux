import sys
import asyncio
import pytest

from flux.runner import process_mgr
from flux.debouncer import ReloadSignal

@pytest.mark.asyncio
async def test_process_mgr_start_and_restart(tmp_path):
    reload_q = asyncio.Queue()
    ui_q     = asyncio.Queue()

    cmd = [
        sys.executable, "-u", "-c",
        "import time;print('hello');time.sleep(0.05);print('world')"
    ]

    task = asyncio.create_task(process_mgr(reload_q, ui_q, cmd))

    try:
        evt = await asyncio.wait_for(ui_q.get(), timeout=1.0)
        assert evt[0] == "proc_started"
        pid1 = evt[1]
        assert isinstance(pid1, int)

        line1 = await asyncio.wait_for(ui_q.get(), timeout=1.0)
        assert line1 == ("stdout", "hello\n")
        line2 = await asyncio.wait_for(ui_q.get(), timeout=1.0)
        assert line2 == ("stdout", "world\n")

        await reload_q.put(ReloadSignal())

        exited = await asyncio.wait_for(ui_q.get(), timeout=1.0)
        assert exited[0] == "proc_exited"
        assert isinstance(exited[1], int)

        evt2 = await asyncio.wait_for(ui_q.get(), timeout=1.0)
        assert evt2[0] == "proc_started"
        pid2 = evt2[1]
        assert isinstance(pid2, int) and pid2 != pid1

    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
