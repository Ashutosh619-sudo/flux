# tests/test_watcher.py

import time
import pytest
from pathlib import Path
from watchdog.events import FileCreatedEvent
from flux.watcher import WatchdogWatcher

@pytest.mark.flaky(reruns=2, reruns_delay=0.2)
def test_watchdog_watcher_detects_file_creation(tmp_path):
    events = []

    def on_event(event):
        events.append(event)

    watcher = WatchdogWatcher(
        watch_paths      = [tmp_path],
        include_patterns = ["*.txt"],
        ignore_patterns  = [],
        on_event         = on_event,
    )
    watcher.start()
    try:
        (tmp_path / "hello.txt").write_text("👋")
        time.sleep(0.5)
    finally:
        watcher.stop()

    assert any(
        isinstance(e, FileCreatedEvent) and e.src_path.endswith("hello.txt")
        for e in events
    ), f"No FileCreatedEvent for hello.txt; got: {events}"


@pytest.mark.flaky(reruns=2, reruns_delay=0.2)
def test_watchdog_watcher_respects_ignore_pattern(tmp_path):
    events = []

    def on_event(event):
        events.append(event)

    watcher = WatchdogWatcher(
        watch_paths      = [tmp_path],
        include_patterns = ["*.txt"],
        ignore_patterns  = ["skip.txt"],
        on_event         = on_event,
    )
    watcher.start()
    try:
        (tmp_path / "skip.txt").write_text("ignore me")
        time.sleep(0.5)

        (tmp_path / "keep.txt").write_text("detect me")
        time.sleep(0.5)
    finally:
        watcher.stop()

    assert not any(
        isinstance(e, FileCreatedEvent) and e.src_path.endswith("skip.txt")
        for e in events
    ), f"skip.txt should have been ignored; got: {[e.src_path for e in events]}"

    assert any(
        isinstance(e, FileCreatedEvent) and e.src_path.endswith("keep.txt")
        for e in events
    ), f"keep.txt should have been detected; got: {events}"
