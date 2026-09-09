import json
import time
import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QSlider, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ftool.config import THEME
from ftool.ui.components import FuturisticCard, NeonButton, StatCard

PROMPT_PRESETS = {
    "🐛 Python Bug Explainer & Fixer": {
        "system": "You are a senior software architect and mentor. Analyze the following code error or bug. Explain what caused it in simple terms for a beginner, provide the corrected code snippet, and list 2 defensive tips to avoid it in the future.",
        "user": "def calculate_average(scores):\n    total = 0\n    for s in scores:\n        total += s\n    return total / len(scores)\n\nprint(calculate_average([])) # Crashes with ZeroDivisionError"
    },
    "⚡ Code Refactoring & Optimization": {
        "system": "You are an expert code optimizer. Refactor the provided code for maximum readability, clean design principles (DRY, SOLID), and algorithmic efficiency.",
        "user": "def find_duplicates(items):\n    dups = []\n    for i in range(len(items)):\n        for j in range(i + 1, len(items)):\n            if items[i] == items[j] and items[i] not in dups:\n                dups.append(items[i])\n    return dups"
    },
    "🗄️ Natural Language to SQL Query": {
        "system": "You are a database engineer. Convert the user's plain English request into an optimized, secure SQL query with proper joins, where clauses, and indexing considerations.",
        "user": "Show me the top 5 customers who spent the most money on electronic products in the year 2024."
    },
    "🔍 Regex Pattern Generator & Explainer": {
        "system": "You are a regular expression specialist. Write a clean regular expression for the requested pattern. Break down each token (flags, character classes, quantifiers, groups) so a beginner can easily understand it.",
        "user": "Match valid IPv4 addresses (0.0.0.0 to 255.255.255.255) and extract the 4 octets."
    },
    "🧠 Machine Learning Explainability": {
        "system": "You are an applied AI researcher. Explain machine learning concepts, metrics, and models in an intuitive, visual manner for someone with no prior math background.",
        "user": "What is the difference between Precision and Recall, and why is high accuracy misleading if my dataset is imbalanced?"
    }
}

class LLMWorker(QThread):
    response_ready = pyqtSignal(str, float)
    error_signal = pyqtSignal(str)

    def __init__(self, endpoint: str, model: str, system_prompt: str, user_prompt: str, temp: float):
        super().__init__()
        self.endpoint = endpoint
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.temp = temp

    def run(self):
        start = time.perf_counter()
        try:
            # Check if local Ollama
            if "localhost:11434" in self.endpoint or "127.0.0.1:11434" in self.endpoint:
                url = f"{self.endpoint}/api/generate"
                payload = {
                    "model": self.model,
                    "prompt": f"<system>\n{self.system_prompt}\n</system>\n<user>\n{self.user_prompt}\n</user>",
                    "stream": False,
                    "options": {"temperature": self.temp}
                }
                resp = requests.post(url, json=payload, timeout=30)
                elapsed = (time.perf_counter() - start) * 1000.0
                if resp.status_code == 200:
                    text = resp.json().get("response", "(No response text)")
                    self.response_ready.emit(text, round(elapsed, 1))
                else:
                    self.error_signal.emit(f"Ollama returned status {resp.status_code}: {resp.text}")
            else:
                # Simulated local offline intelligence fallback
                elapsed = (time.perf_counter() - start) * 1000.0
                simulated_reply = (
                    f"### [FTool AI Engine - Offline Evaluation Mode]\n\n"
                    f"**Analysis of User Query:**\n\n"
                    f"> `{self.user_prompt.splitlines()[0][:60]}...`\n\n"
                    f"**Guidance & Recommendations:**\n"
                    f"1. **Root Cause Analysis**: The logic should be protected against edge cases (e.g. empty collections, null pointers, unescaped regex characters).\n"
                    f"2. **Best Practice Fix**: Always validate preconditions and bounds before execution.\n"
                    f"3. **Local AI Engine**: To activate live local LLM inference, install [Ollama](https://ollama.com) on your machine (`ollama run llama3` or `mistral`), and FTool will automatically connect to `http://localhost:11434`!\n\n"
                    f"*(Tokens Processed: ~{len(self.user_prompt.split()) + 40} tokens | Response Latency: {elapsed:.1f}ms)*"
                )
                self.response_ready.emit(simulated_reply, round(elapsed, 1))
        except Exception as e:
            self.error_signal.emit(str(e))


class LLMStudioTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Header Config Card
        top_card = FuturisticCard("AI PROMPT STUDIO & LOCAL LLM CONTROLLER")
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        top_layout.addWidget(QLabel("Preset:"))
        self.combo_presets = QComboBox()
        self.combo_presets.addItems(list(PROMPT_PRESETS.keys()))
        self.combo_presets.currentIndexChanged.connect(self._on_preset_change)
        top_layout.addWidget(self.combo_presets)

        top_layout.addWidget(QLabel("Endpoint:"))
        self.llm_endpoint = QLineEdit("http://localhost:11434")
        self.llm_endpoint.setFixedWidth(180)
        top_layout.addWidget(self.llm_endpoint)

        top_layout.addWidget(QLabel("Model:"))
        self.llm_model = QLineEdit("llama3")
        self.llm_model.setFixedWidth(90)
        top_layout.addWidget(self.llm_model)

        self.btn_send = NeonButton("⚡ GENERATE PROMPT", variant="green")
        self.btn_send.clicked.connect(self._generate_llm)
        top_layout.addWidget(self.btn_send)

        btn_detect = NeonButton("Detect Ollama", variant="cyan")
        btn_detect.clicked.connect(self._detect_ollama)
        top_layout.addWidget(btn_detect)

        top_layout.addStretch()

        self.stat_latency = StatCard("Latency", "0 ms", color=THEME['accent_cyan'])
        self.stat_tokens = StatCard("Est. Tokens", "0", color=THEME['accent_purple'])
        self.stat_latency.setFixedHeight(50)
        self.stat_tokens.setFixedHeight(50)
        top_layout.addWidget(self.stat_latency)
        top_layout.addWidget(self.stat_tokens)

        top_card.addLayout(top_layout)
        main_layout.addWidget(top_card)

        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Column: System & User Prompt Inputs
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(10)

        sys_card = FuturisticCard("SYSTEM INSTRUCTION (AI PERSONA & GUARDRAILS)")
        self.txt_sys = QTextEdit()
        sys_card.addWidget(self.txt_sys)
        left_layout.addWidget(sys_card)

        user_card = FuturisticCard("USER PROMPT & TASK INPUT")
        self.txt_user = QTextEdit()
        self.txt_user.textChanged.connect(self._update_token_estimate)
        user_card.addWidget(self.txt_user)
        left_layout.addWidget(user_card)

        splitter.addWidget(left_widget)

        # Right Column: AI Output Response
        out_card = FuturisticCard("AI GENERATION & INSIGHT OUTPUT")
        self.txt_out = QTextEdit()
        self.txt_out.setReadOnly(True)
        self.txt_out.setFontFamily("Consolas")
        self.txt_out.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['bg_dark']};
                color: #f1f5f9;
                border: 1px solid {THEME['border_subtle']};
                padding: 12px;
                font-size: 13px;
            }}
        """)
        out_card.addWidget(self.txt_out)
        splitter.addWidget(out_card)

        main_layout.addWidget(splitter)

        # Load initial preset
        self._on_preset_change(0)

    def _on_preset_change(self, idx: int):
        key = list(PROMPT_PRESETS.keys())[idx]
        preset = PROMPT_PRESETS[key]
        self.txt_sys.setPlainText(preset["system"])
        self.txt_user.setPlainText(preset["user"])
        self._update_token_estimate()

    def _update_token_estimate(self):
        words = len(self.txt_user.toPlainText().split()) + len(self.txt_sys.toPlainText().split())
        approx_tokens = int(words * 1.3)
        self.stat_tokens.set_value(str(approx_tokens))

    def _detect_ollama(self):
        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=2)
            if resp.status_code == 200:
                models = [m.get("name") for m in resp.json().get("models", [])]
                if models:
                    self.llm_model.setText(models[0])
                    QMessageBox.information(self, "Ollama Detected", f"Ollama is running locally!\nInstalled models: {', '.join(models)}")
                else:
                    QMessageBox.information(self, "Ollama Detected", "Ollama is running, but no models are downloaded yet.\nRun 'ollama run llama3' in terminal.")
            else:
                QMessageBox.warning(self, "Ollama Check", "Ollama responded with non-200 code.")
        except Exception:
            QMessageBox.information(self, "Ollama Status", "Local Ollama server not detected at http://localhost:11434.\nOffline simulation mode will be used.")

    def _generate_llm(self):
        sys_p = self.txt_sys.toPlainText().strip()
        user_p = self.txt_user.toPlainText().strip()
        if not user_p:
            return

        self.btn_send.setEnabled(False)
        self.btn_send.setText("GENERATING...")
        self.txt_out.setPlainText("Processing neural prompt...")

        self.worker = LLMWorker(
            endpoint=self.llm_endpoint.text().strip(),
            model=self.llm_model.text().strip(),
            system_prompt=sys_p,
            user_prompt=user_p,
            temp=0.7
        )
        self.worker.response_ready.connect(self._on_llm_ready)
        self.worker.error_signal.connect(self._on_llm_error)
        self.worker.start()

    def _on_llm_ready(self, text: str, latency: float):
        self.btn_send.setEnabled(True)
        self.btn_send.setText("⚡ GENERATE PROMPT")
        self.stat_latency.set_value(f"{latency} ms")
        self.txt_out.setMarkdown(text)

    def _on_llm_error(self, err: str):
        self.btn_send.setEnabled(True)
        self.btn_send.setText("⚡ GENERATE PROMPT")
        self.txt_out.setPlainText(f"Error: {err}")
