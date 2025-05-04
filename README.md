# Flux

**Universal Hot-Reload Manager**

Flux is a cross-platform, language-agnostic CLI tool that watches your code and automatically restarts **any** shell command when files change. It ships with zero-config defaults, optional TOML/YAML configuration, and a Rich-powered TUI for live logs and timing.

---

## 🚀 Features

- **Universal watcher**: wrap _any_ command (servers, test runners, compilers, file sync, etc.)  
- **Zero-config**: sensible defaults (watch `./`, ignore `.git/`, `venv/`, `node_modules/`, all extensions, 200 ms debounce)  
- **Config file support**: `hotreload.toml` or `hotreload.yaml` for persistent settings  
- **Flexible CLI flags**: override paths, ignore patterns, extensions, debounce interval, and command  
- **Debounced restarts**: coalesce rapid file changes into a single restart  
- **Cross-platform**: Linux (inotify), macOS (FSEvents), Windows (ReadDirectoryChangesW)  
- **Rich TUI**: color-coded stdout vs stderr, process status indicator, and runtime timer  

---

## 💾 Installation

PyPI link:
https://pypi.org/project/flux-reload/

From PyPI:

```bash
pip install flux
```

From source (editable mode):

```bash
git clone https://github.com/yourusername/flux.git
cd flux
pip install -e .
```

---

## ⚡ Quick Start

Wrap your existing command:

```bash
flux -- python server.py --port 8080
```

Flux will watch the current directory (`.`), ignore common folders, and restart your process whenever any file changes, showing logs and restart timings in its built-in TUI.

---

## 📖 CLI Usage

```text
Usage: flux [OPTIONS] -- <command>...

Options:
  -w, --watch PATH      Paths to watch (repeatable)
  -i, --ignore PATH     Paths to ignore (repeatable)
      --exts TEXT       Comma-separated extensions (e.g. py,html)
      --debounce INT    Debounce interval in milliseconds (default: 200)
  -c, --config PATH     Path to hotreload.toml or .yaml
  --help                Show this message and exit
```

### Examples

```bash
# Watch src/ and templates/, ignore tests/
flux -w src -w templates -i tests -- python app.py

# Only trigger on .py and .html changes
flux --exts py,html -- python app.py

# Increase debounce to 500 ms
flux --debounce 500 -- python app.py

# Using a config file
flux -c hotreload.toml
```

---

## ⚙️ Configuration File

Drop a `hotreload.toml` or `hotreload.yaml` in your project root:

```toml
# hotreload.toml
watch       = ["src/", "templates/"]
ignore      = ["tests/", "venv/"]
exts        = ["py", "html"]
debounce_ms = 300
cmd         = ["python", "app.py", "--port", "8080"]
```

```yaml
# hotreload.yaml
watch:
  - src/
  - templates/
ignore:
  - tests/
  - venv/
exts:
  - py
  - html
debounce_ms: 300
cmd:
  - python
  - app.py
  - --port
  - "8080"
```

Then simply:

```bash
flux -c hotreload.toml
```

Flux will pick up all your settings and run your command with automatic reloads.

---

## 🏗 Architecture Overview

Flux is built as an **async event-driven pipeline**:

1. **Watcher**  
   Uses `watchdog` to observe filesystem changes and pushes events into an `asyncio.Queue`.  
2. **Debouncer**  
   Coalesces rapid bursts of events into a single `ReloadSignal`.  
3. **Process Manager**  
   Gracefully kills & restarts your wrapped command via `asyncio.create_subprocess_exec`.  
4. **Renderer**  
   Renders a Rich TUI: color-coded logs, ▶️/⏸ status icon, and restart timers.

Each stage is decoupled by queues, adheres to SOLID principles, and is easy to unit-test or extend.

---

## 🤝 Contributing

1. Fork the repo  
2. Create a feature branch:  
   ```bash
   git checkout -b feat/my-feature
   ```  
3. Commit your changes & add tests  
4. Open a Pull Request  

Please follow the existing code style, write tests for new features, and ensure the TUI remains responsive.
