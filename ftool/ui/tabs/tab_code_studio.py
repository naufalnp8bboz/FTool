from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSplitter, QTextEdit, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ftool.config import THEME
from ftool.ui.components import FuturisticCard, NeonButton, FuturisticCodeEditor, StatCard
from ftool.core.code_engine import CodeEngine

PRESET_SCRIPTS = {
    "⚡ Quickstart / Hello World": '''# Welcome to FTool Code Studio
import sys

def greet(name: str) -> str:
    """Returns a greeting."""
    return f"Hello, {name}! Welcome to FTool 1.0."

message = greet("Cyber Explorer")
print(message)
print(f"Running on Python {sys.version.split()[0]}")
''',

    "📊 Data Science & Statistics": '''import numpy as np

# Generate random normal distribution
data = np.random.normal(loc=50.0, scale=10.0, size=1000)

print(f"Sample Size: {len(data)}")
print(f"Mean: {np.mean(data):.3f}")
print(f"Std Dev: {np.std(data):.3f}")
print(f"Min: {np.min(data):.3f} | Max: {np.max(data):.3f}")
print(f"95th Percentile: {np.percentile(data, 95):.3f}")
''',

    "🧮 Prime Numbers & Algorithms": '''def sieve_of_eratosthenes(limit: int):
    primes = []
    is_prime = [True] * (limit + 1)
    for p in range(2, limit + 1):
        if is_prime[p]:
            primes.append(p)
            for i in range(p * p, limit + 1, p):
                is_prime[i] = False
    return primes

limit = 100
primes = sieve_of_eratosthenes(limit)
print(f"Primes up to {limit}:")
print(primes)
print(f"Total count: {len(primes)}")
'''
}

class CodeExecutionWorker(QThread):
    finished_execution = pyqtSignal(dict)

    def __init__(self, code_str: str):
        super().__init__()
        self.code_str = code_str

    def run(self):
        result = CodeEngine.execute_python_code(self.code_str)
        self.finished_execution.emit(result)


class CodeStudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Top Control Bar
        top_bar = FuturisticCard()
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)

        top_layout.addWidget(QLabel("Templates:"))
        self.combo_presets = QComboBox()
        self.combo_presets.addItems(list(PRESET_SCRIPTS.keys()))
        self.combo_presets.currentIndexChanged.connect(self._load_preset)
        top_layout.addWidget(self.combo_presets)

        self.btn_run = NeonButton("▶ RUN CODE", variant="green")
        self.btn_run.clicked.connect(self._run_code)
        top_layout.addWidget(self.btn_run)

        btn_ast = NeonButton("🔍 Inspect AST", variant="cyan")
        btn_ast.clicked.connect(self._inspect_ast)
        top_layout.addWidget(btn_ast)

        btn_clear = NeonButton("Clear Console", variant="purple")
        btn_clear.clicked.connect(self._clear_console)
        top_layout.addWidget(btn_clear)

        top_layout.addStretch()

        self.stat_time = StatCard("Execution Time", "0 ms", color=THEME['accent_cyan'])
        self.stat_time.setFixedHeight(50)
        top_layout.addWidget(self.stat_time)

        top_bar.addLayout(top_layout)
        main_layout.addWidget(top_bar)

        # Editor and Output Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background-color: #1d2942; height: 4px; }")

        # Code Editor Container
        editor_card = FuturisticCard("PYTHON SCRIPT EDITOR")
        self.editor = FuturisticCodeEditor()
        editor_card.addWidget(self.editor)
        splitter.addWidget(editor_card)

        # Output / Analysis Tab Container
        bottom_card = FuturisticCard("EXECUTION & STRUCTURE CONSOLE")
        self.bottom_tabs = QTabWidget()

        # Terminal Output Tab
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFontFamily("Consolas")
        self.console_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['bg_dark']};
                color: #e2e8f0;
                border: 1px solid {THEME['border_subtle']};
                padding: 8px;
            }}
        """)
        self.bottom_tabs.addTab(self.console_output, "Terminal Output")

        # AST Inspector Tab
        self.ast_output = QTextEdit()
        self.ast_output.setReadOnly(True)
        self.ast_output.setFontFamily("Consolas")
        self.ast_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['bg_dark']};
                color: {THEME['accent_cyan']};
                border: 1px solid {THEME['border_subtle']};
                padding: 8px;
            }}
        """)
        self.bottom_tabs.addTab(self.ast_output, "AST Structure Tree")

        bottom_card.addWidget(self.bottom_tabs)
        splitter.addWidget(bottom_card)

        main_layout.addWidget(splitter)

        # Load initial preset
        self._load_preset(0)

    def _load_preset(self, index: int):
        key = list(PRESET_SCRIPTS.keys())[index]
        self.editor.setPlainText(PRESET_SCRIPTS[key])

    def _run_code(self):
        code_str = self.editor.toPlainText()
        if not code_str.strip():
            return

        self.btn_run.setEnabled(False)
        self.btn_run.setText("RUNNING...")
        self.console_output.append(f"<span style='color:{THEME['text_muted']};'>--- Executing code block ---</span>")

        self.worker = CodeExecutionWorker(code_str)
        self.worker.finished_execution.connect(self._on_execution_done)
        self.worker.start()

    def _on_execution_done(self, res: dict):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("▶ RUN CODE")

        self.stat_time.set_value(f"{res['execution_time_ms']} ms")
        self.bottom_tabs.setCurrentIndex(0)

        if res["stdout"]:
            self.console_output.append(f"<pre style='color:{THEME['accent_green']};'>{res['stdout'].strip()}</pre>")

        if res["stderr"]:
            self.console_output.append(f"<pre style='color:{THEME['accent_red']};'>{res['stderr'].strip()}</pre>")

        if not res["stdout"] and not res["stderr"]:
            self.console_output.append(f"<span style='color:{THEME['text_secondary']};'>(Code executed with no output)</span>")

    def _inspect_ast(self):
        code_str = self.editor.toPlainText()
        analysis = CodeEngine.analyze_python_ast(code_str)
        self.bottom_tabs.setCurrentIndex(1)

        if "error" in analysis:
            self.ast_output.setPlainText(analysis["error"])
            return

        out = []
        out.append(f"TOTAL LINES: {analysis['total_lines']}")
        out.append("\nIMPORTS DETECTED:")
        if analysis["imports"]:
            for imp in analysis["imports"]:
                out.append(f"  • {imp}")
        else:
            out.append("  (None)")

        out.append("\nFUNCTIONS DETECTED:")
        if analysis["functions"]:
            for fn in analysis["functions"]:
                out.append(f"  • def {fn['name']}({', '.join(fn['args'])}) [Line {fn['line']}]")
                out.append(f"    Docstring: {fn['docstring']}")
        else:
            out.append("  (None)")

        out.append("\nCLASSES DETECTED:")
        if analysis["classes"]:
            for cls in analysis["classes"]:
                out.append(f"  • class {cls['name']} [Line {cls['line']}]")
                out.append(f"    Methods: {', '.join(cls['methods'])}")
        else:
            out.append("  (None)")

        self.ast_output.setPlainText("\n".join(out))

    def _clear_console(self):
        self.console_output.clear()
