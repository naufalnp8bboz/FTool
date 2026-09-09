import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QCheckBox, QTabWidget, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from ftool.config import THEME
from ftool.ui.components import FuturisticCard, NeonButton, StatCard
from ftool.core.code_engine import CodeEngine

class DevToolsTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        self.tabs = QTabWidget()

        # 1. Regex Studio
        self.tabs.addTab(self._build_regex_tab(), "🔍 Regex Sandbox")

        # 2. API / Webhook Requester
        self.tabs.addTab(self._build_api_tab(), "🌐 API & Webhook Tester")

        # 3. Encoders & Hash Swiss-Army
        self.tabs.addTab(self._build_encoders_tab(), "🔐 Encoders & Hashes")

        main_layout.addWidget(self.tabs)

    # ------------------ REGEX STUDIO ------------------ #
    def _build_regex_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        top_card = FuturisticCard("REGEX PATTERN & CONFIG")
        p_layout = QHBoxLayout()
        self.reg_pattern = QLineEdit(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        self.reg_pattern.setPlaceholderText("Enter regular expression (e.g. \\d{3}-\\d{4})...")
        p_layout.addWidget(QLabel("Pattern:"))
        p_layout.addWidget(self.reg_pattern)

        self.reg_case = QCheckBox("Ignore Case")
        self.reg_case.setChecked(True)
        self.reg_case.stateChanged.connect(self._run_regex)
        p_layout.addWidget(self.reg_case)

        self.reg_multi = QCheckBox("Multiline")
        self.reg_multi.stateChanged.connect(self._run_regex)
        p_layout.addWidget(self.reg_multi)

        btn_run = NeonButton("Match Regex", variant="cyan")
        btn_run.clicked.connect(self._run_regex)
        p_layout.addWidget(btn_run)

        top_card.addLayout(p_layout)
        layout.addWidget(top_card)

        # Splitter: Text input and match results
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Test String Card
        str_card = FuturisticCard("TEST STRING")
        self.reg_text = QTextEdit()
        self.reg_text.setPlainText(
            "Contact our support team at support@ftech.dev or reach out to security-team@domain.org for inquiries. "
            "Invalid emails like user@.com or @domain will not match."
        )
        self.reg_text.textChanged.connect(self._run_regex)
        str_card.addWidget(self.reg_text)
        splitter.addWidget(str_card)

        # Match Results Table
        res_card = FuturisticCard("MATCHED TOKENS & CAPTURE GROUPS")
        self.reg_table = QTableWidget()
        self.reg_table.setColumnCount(4)
        self.reg_table.setHorizontalHeaderLabels(["#", "Match Value", "Span (Start - End)", "Groups"])
        self.reg_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        res_card.addWidget(self.reg_table)
        splitter.addWidget(res_card)

        layout.addWidget(splitter)
        self._run_regex()
        return widget

    def _run_regex(self):
        pattern = self.reg_pattern.text()
        text = self.reg_text.toPlainText()
        res = CodeEngine.test_regex(
            pattern, text,
            ignore_case=self.reg_case.isChecked(),
            multiline=self.reg_multi.isChecked()
        )

        self.reg_table.setRowCount(0)
        if not res["success"]:
            self.reg_table.setRowCount(1)
            self.reg_table.setItem(0, 1, QTableWidgetItem(f"Regex Error: {res.get('error')}"))
            return

        matches = res.get("matches", [])
        self.reg_table.setRowCount(len(matches))
        for i, m in enumerate(matches):
            self.reg_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.reg_table.setItem(i, 1, QTableWidgetItem(m["match"]))
            self.reg_table.setItem(i, 2, QTableWidgetItem(f"[{m['start']} : {m['end']}]"))
            self.reg_table.setItem(i, 3, QTableWidgetItem(str(m["groups"])))

    # ------------------ API TESTER ------------------ #
    def _build_api_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Request Line
        req_card = FuturisticCard("HTTP REQUEST BUILDER")
        req_layout = QHBoxLayout()
        self.api_method = QComboBox()
        self.api_method.addItems(["GET", "POST", "PUT", "DELETE"])
        self.api_method.setFixedWidth(90)

        self.api_url = QLineEdit("https://httpbin.org/get")
        self.api_url.setPlaceholderText("Enter API endpoint (https://...)")

        btn_send = NeonButton("⚡ SEND REQUEST", variant="green")
        btn_send.clicked.connect(self._send_api_request)

        req_layout.addWidget(self.api_method)
        req_layout.addWidget(self.api_url)
        req_layout.addWidget(btn_send)
        req_card.addLayout(req_layout)
        layout.addWidget(req_card)

        # Stats Bar (Status code, Latency)
        stats_row = QHBoxLayout()
        self.stat_status = StatCard("Status Code", "-", color=THEME['accent_cyan'])
        self.stat_latency = StatCard("Latency", "- ms", color=THEME['accent_purple'])
        stats_row.addWidget(self.stat_status)
        stats_row.addWidget(self.stat_latency)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        # Splitter: Request Body/Headers | Response Body
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Request payload
        left_card = FuturisticCard("REQUEST HEADERS & BODY (OPTIONAL)")
        self.api_body = QTextEdit()
        self.api_body.setPlaceholderText('{\n  "key": "value"\n}')
        left_card.addWidget(self.api_body)
        splitter.addWidget(left_card)

        # Response payload
        right_card = FuturisticCard("RESPONSE BODY & HEADERS")
        self.api_resp = QTextEdit()
        self.api_resp.setReadOnly(True)
        self.api_resp.setFontFamily("Consolas")
        right_card.addWidget(self.api_resp)
        splitter.addWidget(right_card)

        layout.addWidget(splitter)
        return widget

    def _send_api_request(self):
        method = self.api_method.currentText()
        url = self.api_url.text().strip()
        body = self.api_body.toPlainText().strip() or None

        self.api_resp.setPlainText("Sending request...")
        res = CodeEngine.send_http_request(url, method=method, data_str=body)

        self.stat_status.set_value(str(res["status_code"]))
        self.stat_latency.set_value(f"{res['latency_ms']} ms")
        self.api_resp.setPlainText(res["body"])

    # ------------------ ENCODERS & HASHES ------------------ #
    def _build_encoders_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        card = FuturisticCard("SWISS-ARMY ENCODERS, DECODERS & CRYPTO HASHES")
        c_layout = QVBoxLayout()

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Operation:"))
        self.combo_ops = QComboBox()
        self.combo_ops.addItems([
            "Base64 Encode", "Base64 Decode",
            "SHA-256 Hash", "MD5 Hash",
            "URL Encode", "URL Decode",
            "Hex Encode", "Hex Decode",
            "JWT Token Decode"
        ])
        top_row.addWidget(self.combo_ops)

        btn_convert = NeonButton("⚡ CONVERT", variant="cyan")
        btn_convert.clicked.connect(self._run_conversion)
        top_row.addWidget(btn_convert)

        btn_json_format = NeonButton("Format JSON", variant="purple")
        btn_json_format.clicked.connect(self._format_json)
        top_row.addWidget(btn_json_format)

        top_row.addStretch()
        c_layout.addLayout(top_row)

        # Input / Output
        io_splitter = QSplitter(Qt.Orientation.Vertical)

        in_card = FuturisticCard("INPUT TEXT")
        self.txt_enc_in = QTextEdit()
        self.txt_enc_in.setPlainText("FTech: Futuristic Intelligent Tools for Everyone")
        in_card.addWidget(self.txt_enc_in)
        io_splitter.addWidget(in_card)

        out_card = FuturisticCard("OUTPUT RESULT")
        self.txt_enc_out = QTextEdit()
        self.txt_enc_out.setReadOnly(True)
        self.txt_enc_out.setFontFamily("Consolas")
        out_card.addWidget(self.txt_enc_out)
        io_splitter.addWidget(out_card)

        c_layout.addWidget(io_splitter)
        card.addLayout(c_layout)
        layout.addWidget(card)

        self._run_conversion()
        return widget

    def _run_conversion(self):
        text = self.txt_enc_in.toPlainText()
        op = self.combo_ops.currentText()
        mapping = {
            "Base64 Encode": "base64_encode",
            "Base64 Decode": "base64_decode",
            "SHA-256 Hash": "sha256",
            "MD5 Hash": "md5",
            "URL Encode": "url_encode",
            "URL Decode": "url_decode",
            "Hex Encode": "hex_encode",
            "Hex Decode": "hex_decode",
            "JWT Token Decode": "jwt_decode",
        }
        res = CodeEngine.convert_string(text, mapping.get(op, "base64_encode"))
        self.txt_enc_out.setPlainText(res)

    def _format_json(self):
        text = self.txt_enc_in.toPlainText()
        res = CodeEngine.format_json(text)
        if res["success"]:
            self.txt_enc_out.setPlainText(res["result"])
        else:
            self.txt_enc_out.setPlainText(f"JSON Format Error: {res.get('error')}")
