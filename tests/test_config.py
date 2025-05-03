# Updated tests/test_config.py

import pytest
from pathlib import Path
from flux.config import load_settings

def test_load_settings_overrides_cli_args():
    # No config file—everything comes from the overrides
    settings = load_settings(
        watch_paths=["src", "tests"],
        ignore_paths=["venv", ".git"],
        exts=["py", "md"],
        debounce_ms=500,
        cmd=["python", "app.py"],
    )

    assert settings.watch_paths  == [Path("src"),  Path("tests")]
    assert settings.ignore_paths == [Path("venv"), Path(".git")]
    assert settings.exts          == {"py", "md"}
    assert settings.debounce_ms   == 500
    assert settings.cmd           == ["python", "app.py"]


def test_load_settings_from_toml(tmp_path):
    # Create a temporary TOML config file
    toml_path = tmp_path / "hotreload.toml"
    toml_path.write_text(
        """
        watch        = ["app", "lib"]
        ignore       = [".cache"]
        exts         = ["py"]
        debounce_ms  = 300
        cmd          = ["pytest", "-q"]
        """
    )

    settings = load_settings(
        config_path=toml_path,
    )

    assert settings.watch_paths  == [Path("app"), Path("lib")]
    assert settings.ignore_paths == [Path(".cache")]
    assert settings.exts          == {"py"}
    assert settings.debounce_ms   == 300
    assert settings.cmd           == ["pytest", "-q"]


def test_cli_overrides_toml(tmp_path):
    # TOML provides some defaults...
    toml_path = tmp_path / "cfg.toml"
    toml_path.write_text(
        """
        watch       = ["app"]
        debounce_ms = 100
        """
    )

    # …but CLI overrides should take precedence
    settings = load_settings(
        config_path  = toml_path,
        watch_paths  = ["src"],
        debounce_ms  = 200,
    )

    assert settings.watch_paths == [Path("src")]
    assert settings.debounce_ms  == 200
