# tests/test_debouncer.py

import asyncio
import pytest
from flux.debouncer import debouncer, ReloadSignal

@pytest.mark.asyncio
async def test_single_event_triggers_one_reload():
    raw_q = asyncio.Queue()
    reload_q = asyncio.Queue()

    debounce_ms = 20

    task = asyncio.create_task(debouncer(raw_q, reload_q, debounce_ms))

    await raw_q.put(object())

    sig = await asyncio.wait_for(reload_q.get(), timeout=0.5)
    assert isinstance(sig, ReloadSignal)

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(reload_q.get(), timeout=debounce_ms / 1000 * 1.5)

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_rapid_events_still_single_reload():
    raw_q = asyncio.Queue()
    reload_q = asyncio.Queue()
    debounce_ms = 20
    task = asyncio.create_task(debouncer(raw_q, reload_q, debounce_ms))

    for _ in range(5):
        await raw_q.put(object())

    sig = await asyncio.wait_for(reload_q.get(), timeout=0.5)
    assert isinstance(sig, ReloadSignal)

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(reload_q.get(), timeout=debounce_ms / 1000 * 1.5)

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_two_bursts_trigger_two_reloads():
    raw_q = asyncio.Queue()
    reload_q = asyncio.Queue()
    debounce_ms = 20
    task = asyncio.create_task(debouncer(raw_q, reload_q, debounce_ms))

    await raw_q.put(object())
    sig1 = await asyncio.wait_for(reload_q.get(), timeout=0.5)
    assert isinstance(sig1, ReloadSignal)

    await asyncio.sleep(debounce_ms / 1000 * 2)

    await raw_q.put(object())
    sig2 = await asyncio.wait_for(reload_q.get(), timeout=0.5)
    assert isinstance(sig2, ReloadSignal)

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(reload_q.get(), timeout=debounce_ms / 1000 * 1.5)

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
