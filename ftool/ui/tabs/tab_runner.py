import subprocess
import socket
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ftool.config import THEME
from ftool.ui.components import FuturisticCard, NeonButton

class ProcessWorker(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, cmd: str):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            p = subprocess.Popen(
                self.cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in iter(p.stdout.readline, ''):
                self.output_signal.emit(line)
            p.stdout.close()
            p.wait()
        except Exception as e:
            self.output_signal.emit(f"Execution Error: {e}\n")
        finally:
            self.finished_signal.emit()


class RunnerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Quick Preset Workflow Card
        preset_card = FuturisticCard("AUTOMATED WORKFLOW PRESETS (ZERO TERMINAL FIDDLING)")
        p_layout = QHBoxLayout()
        p_layout.setSpacing(10)

        p_layout.addWidget(QLabel("Preset:"))
        self.combo_presets = QComboBox()
        self.combo_presets.addItems([
            "🐍 Python Runtime Diagnostic",
            "🌐 Local Server Port Scanner (3000, 5000, 8000, 8080)",
            "🌿 Git Repository Status & Log",
            "📦 Pip Top Outdated Packages Check",
            "💻 Custom CLI Command"
        ])
        self.combo_presets.currentIndexChanged.connect(self._on_preset_change)
        p_layout.addWidget(self.combo_presets)

        self.cmd_input = QLineEdit("python --version && python -c \"import sys; print('Executable:', sys.executable)\"")
        p_layout.addWidget(self.cmd_input)

        self.btn_execute = NeonButton("⚡ EXECUTE", variant="cyan")
        self.btn_execute.clicked.connect(self._execute_workflow)
        p_layout.addWidget(self.btn_execute)

        btn_clear = NeonButton("Clear", variant="purple")
        btn_clear.clicked.connect(self._clear_terminal)
        p_layout.addWidget(btn_clear)

        preset_card.addLayout(p_layout)
        main_layout.addWidget(preset_card)

        # Output Terminal
        term_card = FuturisticCard("AUTOMATION EXECUTION TERMINAL")
        self.txt_term = QTextEdit()
        self.txt_term.setReadOnly(True)
        self.txt_term.setFontFamily("Consolas")
        self.txt_term.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['bg_dark']};
                color: {THEME['accent_cyan']};
                border: 1px solid {THEME['border_subtle']};
                padding: 10px;
                font-size: 13px;
            }}
        """)
        term_card.addWidget(self.txt_term)
        main_layout.addWidget(term_card)

    def _on_preset_change(self, idx: int):
        if idx == 0:
            self.cmd_input.setText("python --version && python -c \"import sys, platform; print('Platform:', platform.platform()); print('Python Executable:', sys.executable)\"")
        elif idx == 1:
            self.cmd_input.setText("SCAN_PORTS")
        elif idx == 2:
            self.cmd_input.setText("git status && git log -n 3 --oneline")
        elif idx == 3:
            self.cmd_input.setText("pip list --outdated")
        elif idx == 4:
            self.cmd_input.setText("")

    def _execute_workflow(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return

        self.btn_execute.setEnabled(False)
        self.btn_execute.setText("RUNNING...")
        self.txt_term.append(f"\n<span style='color:#ffffff; font-weight:bold;'>[FTool Engine] Running: {cmd}</span>\n")

        # Custom internal port scanner preset
        if cmd == "SCAN_PORTS":
            self._scan_ports()
            return

        self.worker = ProcessWorker(cmd)
        self.worker.output_signal.connect(self._append_output)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()

    def _scan_ports(self):
        ports = [3000, 5000, 5173, 8000, 8080, 8888]
        self.txt_term.append("Scanning local developer ports (127.0.0.1)...\n")
        open_ports = []
        for port in ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                result = s.connect_ex(('127.0.0.1', port))
                if result == 0:
                    open_ports.append(port)
                    self.txt_term.append(f"  🟢 Port {port}: OPEN (Active local service)")
                else:
                    self.txt_term.append(f"  ⚪ Port {port}: Closed")

        self.txt_term.append(f"\nScan complete. Total active local services: {len(open_ports)}\n")
        self._on_finished()

    def _append_output(self, text: str):
        self.txt_term.insertPlainText(text)
        self.txt_term.ensureCursorVisible()

    def _on_finished(self):
        self.btn_execute.setEnabled(True)
        self.btn_execute.setText("⚡ EXECUTE")
        self.txt_term.append("<span style='color:#00e676;'>✔ Process finished successfully.</span>\n")

    def _clear_terminal(self):
        self.txt_term.clear()
