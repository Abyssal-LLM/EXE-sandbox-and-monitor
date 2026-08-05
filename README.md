# EXE Sandbox

A Windows-native executable sandbox with real-time monitoring and a cyberpunk terminal interface. Launch any EXE in a contained environment and watch every file, registry, network, process, DLL, and memory operation as it happens — with plain English explanations for every output line.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078d4?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

### Monitoring

- **File operations** — open, read, write, create, delete, rename
- **Registry access** — key creation, value modification, enumeration
- **Network connections** — TCP/UDP, DNS queries, data transfers
- **Process lifecycle** — creation, exit, child process spawning, threads
- **DLL loading** — library loads/unloads with path and size tracking
- **Memory usage** — allocation, free, protection changes

### Interface

- **Cyberpunk terminal** — syntax-highlighted, filterable, auto-scrolling
- **Process tree** — live parent-child hierarchy with 500ms refresh
- **Embedded window mode** — reparent the EXE's GUI into the sandbox via `SetParent`
- **Stats panel** — CPU, memory, threads, events, session duration
- **Drag-and-drop EXE loader** with command-line argument support

### Knowledge Base

- **116 entries** across 14 categories explaining every event type, registry key, file path, network port, DLL, and memory operation
- **Click-to-explain** — enable KB mode, click any terminal line, get a plain English explanation
- **Searchable** — filter by keyword, category, or severity
- **Threat context** — security notes for registry keys, ports, and suspicious behaviors

---

## Quick Start

### Prerequisites

- Windows 10/11
- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/Abyssal-LLM/EXE-sandbox-and-monitor.git
cd EXE-sandbox-and-monitor
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

---

## Usage

1. **Drag and drop** an `.exe` onto the loader area, or click to browse
2. Optionally add **command-line arguments** and a **working directory**
3. Toggle **EMBED WINDOW** to embed the EXE's GUI inside the sandbox
4. Click **START** to launch and begin monitoring
5. Watch events stream in the terminal — use the filter checkboxes to focus
6. Toggle **KB** to enable Knowledge Base mode — click any line for an explanation
7. **Right-click** a line → "Explain in Knowledge Base" for a detailed breakdown
8. **Export** logs to a `.txt` file for analysis

---

## Project Structure

```
EXE-sandbox-and-monitor/
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies
├── sandbox/
│   ├── engine.py                    # Orchestrator — ties process manager + monitor
│   ├── process_manager.py           # Windows Job Object containment, CreateProcessW
│   ├── etw_monitor.py               # 8 monitoring threads (file, reg, net, proc, dll, mem, handle, thread)
│   └── events.py                    # EventBus + all event dataclasses
├── gui/
│   ├── main_window.py               # Main window layout + widget wiring
│   ├── theme.py                     # Cyberpunk QSS stylesheet + color palette
│   └── widgets/
│       ├── terminal.py              # Syntax-highlighted terminal with filters
│       ├── process_tree.py          # Live process tree visualization
│       ├── exe_loader.py            # Drag-and-drop EXE selector
│       ├── stats_panel.py           # CPU / Memory / Threads / Events / Duration
│       ├── control_bar.py           # Start / Stop / Clear / Export
│       ├── embedded_window.py       # Window reparenting via SetParent
│       ├── knowledge_base.py        # 116-entry reference database
│       ├── line_explainer.py        # Terminal line parser + NL generator
│       └── reference_tab.py         # Searchable KB browser with explanation panel
└── utils/
    └── helpers.py                   # Shared utilities
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    MainWindow                        │
│  ┌──────────┐  ┌──────────────────────────────────┐ │
│  │ Process   │  │  Terminal  │  Embedded Window    │ │
│  │ Tree      │  │  (events)  │  (EXE GUI)         │ │
│  └──────────┘  └──────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐│
│  │              Stats Panel                          ││
│  └──────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │  SandboxEngine   │
              │  (orchestrator)  │
              └────────┬─────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐    ┌──────────────────────┐
│ ProcessManager   │    │   ETWMonitor         │
│ (Job Objects,    │    │   (8 threads:        │
│  CreateProcessW) │    │    process, file,     │
│                  │    │    net, dll, mem,     │
│                  │    │    registry, handle,  │
│                  │    │    thread)            │
└──────────────────┘    └──────────────────────┘
          │                         │
          └────────────┬────────────┘
                       ▼
              ┌──────────────────┐
              │    EventBus      │
              │ (thread-safe)    │
              └──────────────────┘
```

---

## Monitoring Details

| Category | What It Captures | Technique |
|----------|-----------------|-----------|
| **File** | Open, read, write, create, close, delete | `psutil.Process.open_files()` polling |
| **Registry** | Key create, open, set value, delete, enumerate | `winreg` hive scanning |
| **Network** | TCP/UDP connect, send, receive, close, DNS | `psutil.net_connections()` polling |
| **Process** | Create, exit, child spawn, thread create/exit | `psutil.process_iter()` + `psutil.Process.children()` |
| **DLL** | Load, unload with path and size | `psutil.Process.memory_maps()` polling |
| **Memory** | Alloc, free, protect (RSS/VMS delta) | `psutil.Process.memory_info()` polling |
| **Handles** | Handle count changes | `psutil.Process.num_handles()` |
| **Threads** | Thread count changes | `psutil.Process.threads()` |

---

## Knowledge Base Categories

| Category | Entries | Examples |
|----------|---------|----------|
| Event Types | 6 | FILE, REG, NET, PROC, DLL, MEM |
| File Operations | 7 | CREATE, OPEN, READ, WRITE, CLOSE, DELETE |
| File Paths | 14 | Startup, Temp, System32, Drivers, AppData |
| Registry Operations | 7 | CREATE_KEY, OPEN_KEY, SET_VALUE |
| Registry Keys | 14 | Run, RunOnce, LSA, Defender, Services |
| Network Operations | 7 | TCP_CONNECT, DNS_QUERY, TCP_SEND |
| Network Protocols | 3 | TCP, UDP, ICMP |
| Network Ports | 12 | 21, 22, 23, 53, 80, 443, 445, 3389 |
| Process Operations | 5 | CREATE, EXIT, THREAD_CREATE |
| DLL Operations | 2 | LOAD, UNLOAD |
| DLL Names | 14 | kernel32, ws2_32, advapi32, crypt32 |
| Memory Operations | 5 | ALLOC, FREE, READ, WRITE, PROTECT |
| System Concepts | 9 | Job Objects, ETW, WMI, SetParent |
| Threat Indicators | 11 | Persistence, C2, Ransomware, Injection |

---

## Configuration

Edit `sandbox/engine.py` → `SandboxConfig` to adjust:

```python
self.max_memory_mb: int = 2048        # Memory limit per sandbox
self.max_processes: int = 32           # Max concurrent processes
self.max_cpu_percent: int = 80         # CPU usage cap
self.max_log_lines: int = 10000        # Terminal line limit
```

---

## Requirements

| Package | Version | Purpose |
|---------|---------|---------|
| `PySide6` | >= 6.5.0 | Qt6 GUI framework |
| `pywin32` | >= 306 | Windows API access (Job Objects, SetParent) |
| `psutil` | >= 5.9.0 | Process/system monitoring |

---

## License

MIT License. See [LICENSE](LICENSE) for details.
