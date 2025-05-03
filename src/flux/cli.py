import asyncio
import click

from .config import load_settings
from .app import run_pipeline


@click.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.option("--watch", "-w", multiple=True, type=click.Path(), help="Paths to watch")
@click.option("--ignore", "-i", multiple=True, type=click.Path(), help="Paths to ignore")
@click.option("--exts",    type=str, help="Comma-separated extensions to watch")
@click.option("--debounce", type=int, default=200, help="Debounce interval in ms")
@click.option("--config",  type=click.Path(), help="Path to hotreload.toml/.yaml")
@click.argument("cmd", nargs=-1, type=click.UNPROCESSED)
def main(watch, ignore, exts, debounce, config, cmd):
    """HRM: universal hot-reload manager."""
    settings = load_settings(
        config_path    = config,
        watch_paths    = list(watch),
        ignore_paths   = list(ignore),
        exts           = exts.split(",") if exts else [],
        debounce_ms    = debounce,
        cmd            = list(cmd),
    )

    asyncio.run(run_pipeline(settings))


if __name__ == "__main__":
    main()
