import asyncio
from collections import deque
from datetime import datetime
from typing import Deque, Tuple, Union

from rich.live import Live
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich.console import Console

# A UIEvent is one of:
#   ("stdout" | "stderr" | "proc_started" | "proc_exited", payload)
UIEvent = Tuple[str, Union[int, str]]

async def renderer(
    ui_q: asyncio.Queue[UIEvent],
    max_log_lines: int = 200,
    refresh_rate: float = 10.0,
) -> None:
    """
    Consume UIEvent tuples from ui_q and render them in a Rich Live display.
    Left panel: rolling log. Right panel: status (▶/⏸), PID, uptime, last exit code.
    """
    log_buffer: Deque[Tuple[str, str]] = deque()
    status: str = "⏸ Idle"
    pid: Union[int, None] = None
    start_time: Union[datetime, None] = None
    last_exit: Union[int, None] = None
    last_restart: Union[datetime, None] = None

    console = Console()

    def make_layout():
        total_height = console.size.height
        status_height = 6
        log_height = max(3, total_height - status_height)

        visible = list(log_buffer)[-log_height:]

        log_lines = []
        for label, text in visible:
            prefix = "[green]»[/green]" if label == "stdout" else "[red]!»[/red]"
            log_lines.append(f"{prefix} {text.rstrip()}")
        log_panel = Panel(
            "\n".join(log_lines),
            title=" Logs ",
            border_style="white",
            padding=(1, 2),
            height=log_height,
        )

        table = Table.grid(padding=1)
        table.add_column(justify="right")
        table.add_column()
        table.add_row("Status", status)
        table.add_row("PID", str(pid) if pid else "-")
        if start_time:
            uptime = datetime.now() - start_time
            table.add_row("Uptime", f"{uptime.seconds}s")
        if last_exit is not None:
            table.add_row("Last Exit", str(last_exit))
        if last_restart:
            ago = datetime.now() - last_restart
            table.add_row("Last Reload", f"{ago.seconds}s ago")

        status_panel = Panel(
            table,
            title=" Status ",
            border_style="cyan",
            padding=(1, 2),
        )

        return Columns([log_panel, status_panel], expand=True)

    with Live(make_layout(), refresh_per_second=refresh_rate, screen=False) as live:
        while True:
            try:
                label, payload = await asyncio.wait_for(
                    ui_q.get(), timeout=1 / refresh_rate
                )
            except asyncio.TimeoutError:
                # No new events—just redraw
                live.update(make_layout())
                continue

            now = datetime.now()
            if label in ("stdout", "stderr"):
                log_buffer.append((label, payload))
                pid = payload  
                status = "▶ Running"
                start_time = now
                last_restart = now
            elif label == "proc_exited":
                last_exit = payload
                status = "⏸ Exited"

            live.update(make_layout())
