# src/flux/config.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Optional
import tomllib
import yaml  # ensure you have pyyaml installed

@dataclass
class Settings:
    watch_paths: List[Path] = field(
        default_factory=lambda: [Path(".")]
    )
    ignore_paths: List[Path] = field(
        default_factory=lambda: [Path(".git"), Path("venv"), Path("node_modules")]
    )
    exts: Set[str] = field(default_factory=set)
    debounce_ms: int = 200
    cmd: List[str] = field(default_factory=list)


def _load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def _load_yaml(path: Path) -> dict:
    with path.open("r") as f:
        return yaml.safe_load(f) or {}


def load_config_file(path: Path) -> dict:
    """
    Reads a .toml or .yaml/.yml file and returns its contents as a dict.
    """
    suffix = path.suffix.lower()
    if suffix == ".toml":
        return _load_toml(path)
    if suffix in (".yaml", ".yml"):
        return _load_yaml(path)
    return {}


def load_settings(
    *,
    config_path: Optional[Path] = None,
    watch_paths: Optional[List[str]] = None,
    ignore_paths: Optional[List[str]] = None,
    exts: Optional[List[str]] = None,
    debounce_ms: Optional[int] = None,
    cmd: Optional[List[str]] = None,
) -> Settings:
    """
    Build a Settings object with precedence:
      1) Settings() defaults
      2) Values from the config file (if config_path is given)
      3) Explicit overrides passed via arguments
    """
    settings = Settings()

    if config_path and config_path.exists():
        data = load_config_file(config_path)

        if "watch" in data:
            settings.watch_paths = [Path(p) for p in data["watch"]]
        if "ignore" in data:
            settings.ignore_paths = [Path(p) for p in data["ignore"]]
        if "exts" in data:
            settings.exts = set(data["exts"])
        if "debounce_ms" in data:
            settings.debounce_ms = int(data["debounce_ms"])
        if "cmd" in data:
            settings.cmd = list(data["cmd"])

    if watch_paths:
        settings.watch_paths = [Path(p) for p in watch_paths]
    if ignore_paths:
        settings.ignore_paths = [Path(p) for p in ignore_paths]
    if exts:
        settings.exts = set(exts)
    if debounce_ms is not None:
        settings.debounce_ms = debounce_ms
    if cmd:
        settings.cmd = list(cmd)

    return settings
