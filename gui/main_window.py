"""
Main window for the EXE Sandbox application.
This ties together all the widgets and the sandbox engine into a cohesive GUI.
"""
import os
import time
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QFrame, QLabel, QFileDialog, QMessageBox,
    QApplication, QSizePolicy, QPushButton,
)
from PySide6.QtCore import Qt, Slot, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QColor, QIcon

from gui.theme import (
    NEON_CYAN, NEON_GREEN, NEON_YELLOW, NEON_MAGENTA,
    BG_DEEP_BLACK, BG_DARK, BG_PANEL,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    BORDER_MEDIUM, FONT_FAMILY, get_stylesheet,
)
from sandbox.engine import SandboxEngineScript
from sandbox.events import (
    EventBus, global_event_bus,
    FileEvent, RegistryEvent, NetworkEvent, ProcessEvent, ConsoleEvent,
    ConsoleLevel,
)
from gui.widgets.exe_loader import ExeLoaderWidget
from gui.widgets.terminal import TerminalWidget
from gui.widgets.process_tree import ProcessTreeWidget
from gui.widgets.stats_panel import StatsPanelWidget
from gui.widgets.control_bar import ControlBarWidget
from gui.widgets.embedded_window import EmbeddedWindowWidget
from gui.widgets.reference_tab import ReferenceTabWidget


class SandboxWorker(QThread):
    """
    Background worker thread for sandbox operations.
    This runs the sandbox engine in a separate thread to keep the GUI responsive.
    """
    event_received = Signal(object)
    stats_updated = Signal(dict)

    def __init__(self, engine: SandboxEngineScript, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._running = False

    def run(self):
        """Main worker loop."""
        self._running = True
        while self._running:
            if self.engine.is_running:
                # Update stats
                stats = self.engine.get_stats()
                stats['total_events'] = len(self.engine.event_bus.get_history())
                self.stats_updated.emit(stats)
            time.sleep(0.5)

    def stop(self):
        """Stop the worker loop."""
        self._running = False


class MainWindow(QMainWindow):
    """
    The main application window for the EXE Sandbox.

    This is the top-level container that holds all the widgets and connects
    them to the sandbox engine. It manages the overall application lifecycle.
    """

    def __init__(self):
        super().__init__()

        # Initialize the sandbox engine - this is the brain of the application
        self.engine = SandboxEngineScript()

        # Set up the event bus subscription to receive monitoring events
        self.engine.event_bus.subscribe(self._on_event_received)

        # Set up the UI
        self._setup_ui()
        self._setup_connections()

        # The worker thread for background operations
        self.worker = SandboxWorker(self.engine)
        self.worker.stats_updated.connect(self._on_stats_updated)
        self.worker.start()

    def _setup_ui(self) -> None:
        """Set up the main window UI."""
        # Window properties
        self.setWindowTitle("EXE SANDBOX - Cyberpunk Edition")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Apply the cyberpunk theme
        self.setStyleSheet(get_stylesheet())

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Title bar
        title_layout = QHBoxLayout()
        title_layout.setSpacing(12)

        title_label = QLabel("EXE SANDBOX")
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet(f"""
            color: {NEON_CYAN};
            font-family: '{FONT_FAMILY}', monospace;
            font-size: 24px;
            font-weight: bold;
            letter-spacing: 3px;
        """)
        title_layout.addWidget(title_label)

        subtitle_label = QLabel("// CYBERPUNK MONITORING EDITION")
        subtitle_label.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-family: '{FONT_FAMILY}', monospace;
            font-size: 11px;
            letter-spacing: 1px;
        """)
        title_layout.addWidget(subtitle_label)

        title_layout.addStretch()

        main_layout.addLayout(title_layout)

        # EXE Loader
        self.exe_loader = ExeLoaderWidget()
        main_layout.addWidget(self.exe_loader)

        # Control bar
        self.control_bar = ControlBarWidget()
        main_layout.addWidget(self.control_bar)

        # Main content area with splitter
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setHandleWidth(4)

        # Left side - Process tree
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PANEL};
                border: 1px solid {BORDER_MEDIUM};
                border-radius: 8px;
            }}
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)

        self.process_tree = ProcessTreeWidget()
        left_layout.addWidget(self.process_tree)

        content_splitter.addWidget(left_panel)

        # Right side - Terminal + Embedded Window
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PANEL};
                border: 1px solid {BORDER_MEDIUM};
                border-radius: 8px;
            }}
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)

        # Terminal header with toggle
        terminal_header = QHBoxLayout()
        terminal_title = QLabel("MONITORING TERMINAL")
        terminal_title.setStyleSheet(f"""
            color: {NEON_GREEN};
            font-family: '{FONT_FAMILY}', monospace;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        terminal_header.addWidget(terminal_title)
        terminal_header.addStretch()

        # Toggle button for embedded mode
        self.embed_toggle = QPushButton("EMBED WINDOW")
        self.embed_toggle.setFixedWidth(120)
        self.embed_toggle.setCheckable(True)
        self.embed_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_DEEP_BLACK};
                color: {NEON_CYAN};
                border: 1px solid {NEON_CYAN};
                border-radius: 6px;
                font-family: '{FONT_FAMILY}', monospace;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {NEON_CYAN}15;
            }}
            QPushButton:checked {{
                background-color: {NEON_CYAN}30;
                color: {NEON_CYAN};
            }}
        """)
        self.embed_toggle.clicked.connect(self._on_embed_toggle)
        terminal_header.addWidget(self.embed_toggle)

        # Knowledge Base toggle button
        self.kb_toggle = QPushButton("KB")
        self.kb_toggle.setFixedWidth(40)
        self.kb_toggle.setCheckable(True)
        self.kb_toggle.setToolTip("Toggle Knowledge Base (explains all terminal output)")
        self.kb_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_DEEP_BLACK};
                color: {NEON_MAGENTA};
                border: 1px solid {NEON_MAGENTA};
                border-radius: 6px;
                font-family: '{FONT_FAMILY}', monospace;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {NEON_MAGENTA}15;
            }}
            QPushButton:checked {{
                background-color: {NEON_MAGENTA}30;
                color: {NEON_MAGENTA};
            }}
        """)
        self.kb_toggle.clicked.connect(self._on_kb_toggle)
        terminal_header.addWidget(self.kb_toggle)

        self.event_count_label = QLabel("0 events")
        self.event_count_label.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-family: '{FONT_FAMILY}', monospace;
            font-size: 11px;
        """)
        terminal_header.addWidget(self.event_count_label)

        right_layout.addLayout(terminal_header)

        # Embedded window widget (initially hidden)
        self.embedded_window = EmbeddedWindowWidget()
        self.embedded_window.setMinimumHeight(200)
        self.embedded_window.hide()
        right_layout.addWidget(self.embedded_window)

        # Terminal widget
        self.terminal = TerminalWidget()
        right_layout.addWidget(self.terminal)

        # Reference Database panel (hidden by default)
        self.reference_panel = ReferenceTabWidget()
        self.reference_panel.hide()
        right_layout.addWidget(self.reference_panel)

        content_splitter.addWidget(right_panel)

        # Set splitter proportions
        content_splitter.setSizes([350, 900])

        main_layout.addWidget(content_splitter, 1)  # Stretch factor 1

        # Stats panel at the bottom
        self.stats_panel = StatsPanelWidget()
        main_layout.addWidget(self.stats_panel)

        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background-color: {BG_DARK};
                color: {TEXT_SECONDARY};
                border-top: 1px solid {BORDER_MEDIUM};
                font-family: '{FONT_FAMILY}', monospace;
                font-size: 11px;
            }}
        """)

    def _setup_connections(self) -> None:
        """Set up signal-slot connections between widgets and engine."""
        # EXE loader connections
        self.exe_loader.exe_loaded.connect(self._on_exe_loaded)
        self.exe_loader.exe_cleared.connect(self._on_exe_cleared)

        # Control bar connections
        self.control_bar.start_clicked.connect(self._on_start_clicked)
        self.control_bar.stop_clicked.connect(self._on_stop_clicked)
        self.control_bar.clear_clicked.connect(self._on_clear_clicked)
        self.control_bar.export_clicked.connect(self._on_export_clicked)

        # Terminal export connection
        self.terminal.export_requested.connect(self._on_export_clicked)

        # Terminal explain connection - right-click "Explain" in Knowledge Base
        self.terminal.explain_requested.connect(self._on_explain_requested)

        # Process tree terminate connection
        self.process_tree.terminate_requested.connect(self._on_terminate_requested)

        # Embedded window connections
        self.embedded_window.window_lost.connect(self._on_embedded_window_lost)

    @Slot(str)
    def _on_exe_loaded(self, exe_path: str) -> None:
        """Handle EXE being loaded."""
        self.engine.load_exe(exe_path)
        self.statusBar().showMessage(f"Loaded: {os.path.basename(exe_path)}")

    @Slot()
    def _on_exe_cleared(self) -> None:
        """Handle EXE being cleared."""
        if self.engine.is_running:
            self.engine.stop()
            self.control_bar.set_running(False)
        self.statusBar().showMessage("Ready")

    @Slot()
    def _on_start_clicked(self) -> None:
        """Handle start button click."""
        exe_path = self.exe_loader.get_exe_path()
        if not exe_path:
            QMessageBox.warning(
                self,
                "No EXE Loaded",
                "Please load an EXE file before starting the sandbox."
            )
            return

        args = self.exe_loader.get_args()
        workdir = self.exe_loader.get_workdir()

        # Check if we should embed the window
        embedded = self.embed_toggle.isChecked()

        success = self.engine.start(args, workdir, embedded=embedded)
        if success:
            self.statusBar().showMessage("Sandbox running")

            # If embedded mode, try to embed the window after a delay
            if embedded:
                # Wait for the process to create a window, then embed it
                QTimer.singleShot(1000, self._try_embed_window)
        else:
            QMessageBox.critical(
                self,
                "Failed to Start",
                "Failed to start the sandbox. Check the terminal for details."
            )

    def _try_embed_window(self) -> None:
        """Try to embed the main process window."""
        if not self.engine.is_running:
            return

        pid = self.engine.process_manager.main_pid
        if pid > 0:
            success = self.embedded_window.embed_window_by_pid(pid, timeout=5.0)
            if success:
                self.terminal.append_log(
                    f"[SANDBOX] Window embedded for PID {pid}"
                )
            else:
                self.terminal.append_log(
                    f"[SANDBOX] Could not find window for PID {pid} - process may be console-only"
                )

    @Slot()
    def _on_stop_clicked(self) -> None:
        """Handle stop button click."""
        # Detach the embedded window first
        if self.embedded_window.is_embedded:
            self.embedded_window.detach_window()

        self.engine.stop()
        self.control_bar.set_running(False)
        self.statusBar().showMessage("Sandbox stopped")

    @Slot()
    def _on_embed_toggle(self) -> None:
        """Handle embed toggle button click."""
        if self.embed_toggle.isChecked():
            # Show embedded window, shrink terminal
            self.embedded_window.show()
            self.terminal.setMaximumHeight(250)
            self.statusBar().showMessage("Embedded mode enabled")
        else:
            # Hide embedded window, expand terminal
            if self.embedded_window.is_embedded:
                self.embedded_window.detach_window()
            self.embedded_window.hide()
            self.terminal.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX
            self.statusBar().showMessage("Monitor mode")

    @Slot()
    def _on_kb_toggle(self) -> None:
        """Handle Knowledge Base toggle button click."""
        if self.kb_toggle.isChecked():
            self.reference_panel.show()
            self.terminal.kb_active = True
            self.terminal.setMaximumHeight(250)
            self.statusBar().showMessage("Knowledge Base active — click any terminal line to explain it")
        else:
            self.reference_panel.hide()
            self.terminal.kb_active = False
            self.terminal.setMaximumHeight(16777215)
            self.statusBar().showMessage("Knowledge Base hidden")

    @Slot()
    def _on_clear_clicked(self) -> None:
        """Handle clear button click."""
        self.terminal.clear()
        self.process_tree.clear()
        self.stats_panel.clear()
        self.engine.event_bus.clear_history()
        self.statusBar().showMessage("Cleared")

    @Slot()
    def _on_export_clicked(self) -> None:
        """Handle export button click."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Log",
            f"sandbox_log_{int(time.time())}.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )

        if file_path:
            try:
                log_text = self.terminal.get_log_text()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_text)
                self.statusBar().showMessage(f"Log exported to: {file_path}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export log: {e}"
                )

    @Slot(str)
    def _on_explain_requested(self, line: str) -> None:
        """Handle right-click 'Explain' from terminal — show Knowledge Base with explanation."""
        if not self.kb_toggle.isChecked():
            self.kb_toggle.setChecked(True)
            self._on_kb_toggle()
        self.reference_panel.lookup_line(line)

    @Slot(int)
    def _on_terminate_requested(self, pid: int) -> None:
        """Handle process termination request from context menu."""
        try:
            import psutil
            proc = psutil.Process(pid)
            proc.terminate()
            self.terminal.append_log(
                f"[SANDBOX] Terminated process: {proc.name()}({pid})"
            )
        except Exception as e:
            self.terminal.append_log(
                f"[SANDBOX] Failed to terminate PID {pid}: {e}"
            )

    @Slot()
    def _on_embedded_window_lost(self) -> None:
        """Handle embedded window being closed."""
        self.terminal.append_log(
            "[SANDBOX] Embedded window closed"
        )

    def _on_event_received(self, event) -> None:
        """
        Handle events from the sandbox engine.
        Called from background threads - terminal.append_log is thread-safe via Qt signal.
        """
        log_line = event.to_log_string()
        self.terminal.append_log(log_line)

    @Slot(dict)
    def _on_stats_updated(self, stats: dict) -> None:
        """Handle stats update from the worker thread."""
        self.stats_panel.update_stats(stats)

        # Update the process tree
        process_tree = self.engine.get_process_tree()
        self.process_tree.update_process_tree(process_tree)

        # Update event count
        event_count = len(self.engine.event_bus.get_history())
        self.event_count_label.setText(f"{event_count} events")

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Stop the worker thread
        self.worker.stop()
        self.worker.wait(1000)

        # Clean up the sandbox engine
        self.engine.cleanup()

        # Accept the close event
        event.accept()
