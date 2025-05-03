from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set
import toml
import yaml

@dataclass
class Settings:
    watch_paths: List[Path] = field(default_factory=lambda: [Path('.')])
    ignore_paths: List[Path] = field(default_factory=lambda: [Path('.git'), Path('venv'), Path('node_modules')])
    exts: Set[str] = field(default_factory=set)
    debounce_ms: int = 200
    cmd: List[str] = field(default_factory=list)


def load_config_file(path: Path) -> dict:
    if path.suffix in ('.toml',):
        return toml.load(path)
    elif path.suffix in ('.yaml', '.yml'):
        return yaml.safe_load(path)
    else:
        return {}


def load_settings(config_path: Path = None, **overrides) -> Settings:
    settings = Settings()

    if config_path and config_path.exists():
        data = load_config_file(config_path)
        if 'watch' in data:
            settings.watch_paths = [Path(p) for p in data['watch']]
        if 'ignore' in data:
            settings.ignore_paths = [Path(p) for p in data['ignore']]
        if 'exts' in data:
            settings.exts = set(data['exts'])
        if 'debounce_ms' in data:
            settings.debounce_ms = data['debounce_ms']
        if 'cmd' in data:
            settings.cmd = data['cmd']

    for key, value in overrides.items():
        if value is not None:
            setattr(settings, key, value)

    return settings
