import webbrowser
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ftool.config import THEME
from ftool.ui.components import FuturisticCard, NeonButton, StatCard
from ftool.core.osint_engine import OSINTEngine

class UsernameWorker(QThread):
    results_ready = pyqtSignal(list)

    def __init__(self, username: str):
        super().__init__()
        self.username = username

    def run(self):
        results = OSINTEngine.check_username(self.username)
        self.results_ready.emit(results)


class HeaderAuditWorker(QThread):
    results_ready = pyqtSignal(dict)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        results = OSINTEngine.audit_http_headers(self.url)
        self.results_ready.emit(results)


class ReconTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        self.tabs = QTabWidget()

        # 1. Defensive Web Security Auditor
        self.tabs.addTab(self._build_header_audit_tab(), "🛡️ Web Security & SSL Auditor")

        # 2. Username Scout (Passive Sherlock-style check)
        self.tabs.addTab(self._build_username_scout_tab(), "🔍 Username Footprint Scout")

        # 3. DNS & IP Intelligence
        self.tabs.addTab(self._build_dns_ip_tab(), "🌐 DNS & Geolocation Explorer")

        main_layout.addWidget(self.tabs)

    # ---------------- 1. WEB SECURITY & SSL AUDITOR ---------------- #
    def _build_header_audit_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Input card
        in_card = FuturisticCard("TARGET URL & DEFENSIVE SECURITY AUDIT")
        in_layout = QHBoxLayout()
        self.audit_url = QLineEdit("github.com")
        self.audit_url.setPlaceholderText("Enter target domain or URL (e.g. github.com)...")
        self.btn_audit = NeonButton("⚡ RUN SECURITY AUDIT", variant="cyan")
        self.btn_audit.clicked.connect(self._run_header_audit)
        in_layout.addWidget(QLabel("Target:"))
        in_layout.addWidget(self.audit_url)
        in_layout.addWidget(self.btn_audit)
        in_card.addLayout(in_layout)
        layout.addWidget(in_card)

        # Score & SSL Metrics
        metrics_row = QHBoxLayout()
        self.stat_grade = StatCard("Security Posture Grade", "-", color=THEME['accent_cyan'])
        self.stat_score = StatCard("Defensive Score", "-%", color=THEME['accent_green'])
        self.stat_ssl = StatCard("SSL Certificate Days", "-", color=THEME['accent_purple'])
        self.stat_server = StatCard("Server Banner", "-", color=THEME['accent_amber'])
        metrics_row.addWidget(self.stat_grade)
        metrics_row.addWidget(self.stat_score)
        metrics_row.addWidget(self.stat_ssl)
        metrics_row.addWidget(self.stat_server)
        layout.addLayout(metrics_row)

        # Checklist Table
        table_card = FuturisticCard("DEFENSIVE HTTP HEADERS BREAKDOWN")
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(4)
        self.audit_table.setHorizontalHeaderLabels(["Security Header", "Status", "Importance", "Defensive Role & Explanation"])
        self.audit_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        table_card.addWidget(self.audit_table)
        layout.addWidget(table_card)

        return widget

    def _run_header_audit(self):
        target = self.audit_url.text().strip()
        if not target:
            return

        self.btn_audit.setEnabled(False)
        self.btn_audit.setText("AUDITING...")

        # Also inspect SSL
        ssl_info = OSINTEngine.inspect_ssl(target)
        if ssl_info.get("success"):
            days = ssl_info.get("days_remaining", 0)
            self.stat_ssl.set_value(f"{days} Days")
        else:
            self.stat_ssl.set_value("N/A")

        self.audit_worker = HeaderAuditWorker(target)
        self.audit_worker.results_ready.connect(self._on_audit_done)
        self.audit_worker.start()

    def _on_audit_done(self, res: dict):
        self.btn_audit.setEnabled(True)
        self.btn_audit.setText("⚡ RUN SECURITY AUDIT")

        if not res.get("success"):
            QMessageBox.warning(self, "Audit Error", f"Failed to inspect website:\n{res.get('error')}")
            return

        grade = res.get("grade", "F")
        score = res.get("score_pct", 0)
        server = res.get("server", "Hidden")[:22]

        self.stat_grade.set_value(grade)
        self.stat_score.set_value(f"{score}%")
        self.stat_server.set_value(server)

        checks = res.get("checks", [])
        self.audit_table.setRowCount(len(checks))
        for i, c in enumerate(checks):
            self.audit_table.setItem(i, 0, QTableWidgetItem(c["header"]))
            status_item = QTableWidgetItem("🟢 Present" if c["present"] else "🔴 MISSING")
            self.audit_table.setItem(i, 1, status_item)
            self.audit_table.setItem(i, 2, QTableWidgetItem(c["importance"]))
            self.audit_table.setItem(i, 3, QTableWidgetItem(c["description"]))

    # ---------------- 2. USERNAME SCOUT ---------------- #
    def _build_username_scout_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        in_card = FuturisticCard("PASSIVE USERNAME PUBLIC PROFILE SCOUT")
        in_layout = QHBoxLayout()
        self.user_input = QLineEdit("torvalds")
        self.user_input.setPlaceholderText("Enter target username or handle...")
        self.btn_user_scout = NeonButton("⚡ SCOUT USERNAME", variant="cyan")
        self.btn_user_scout.clicked.connect(self._run_user_scout)
        in_layout.addWidget(QLabel("Username:"))
        in_layout.addWidget(self.user_input)
        in_layout.addWidget(self.btn_user_scout)
        in_card.addLayout(in_layout)
        layout.addWidget(in_card)

        # Progress bar
        self.user_progress = QProgressBar()
        self.user_progress.setFixedHeight(6)
        self.user_progress.setTextVisible(False)
        self.user_progress.setRange(0, 0)
        self.user_progress.setVisible(False)
        layout.addWidget(self.user_progress)

        # Results Table
        res_card = FuturisticCard("PUBLIC PROFILE DISCOVERY RESULTS")
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["Platform", "Status", "Profile URL", "Action"])
        self.user_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        res_card.addWidget(self.user_table)
        layout.addWidget(res_card)

        return widget

    def _run_user_scout(self):
        uname = self.user_input.text().strip()
        if not uname:
            return

        self.btn_user_scout.setEnabled(False)
        self.btn_user_scout.setText("SCOUTING...")
        self.user_progress.setVisible(True)

        self.user_worker = UsernameWorker(uname)
        self.user_worker.results_ready.connect(self._on_user_scout_done)
        self.user_worker.start()

    def _on_user_scout_done(self, results: list):
        self.btn_user_scout.setEnabled(True)
        self.btn_user_scout.setText("⚡ SCOUT USERNAME")
        self.user_progress.setVisible(False)

        self.user_table.setRowCount(len(results))
        for i, r in enumerate(results):
            self.user_table.setItem(i, 0, QTableWidgetItem(r["platform"]))
            status_item = QTableWidgetItem("🟢 FOUND (Active)" if r["exists"] else "⚪ Not Found / Available")
            self.user_table.setItem(i, 1, status_item)
            self.user_table.setItem(i, 2, QTableWidgetItem(r["url"]))

            btn_open = NeonButton("Open Link", variant="purple" if r["exists"] else "cyan")
            btn_open.setEnabled(r["exists"])
            url_to_open = r["url"]
            btn_open.clicked.connect(lambda _, u=url_to_open: webbrowser.open(u))
            self.user_table.setCellWidget(i, 3, btn_open)

    # ---------------- 3. DNS & IP EXPLORER ---------------- #
    def _build_dns_ip_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        in_card = FuturisticCard("DOMAIN DNS & PUBLIC IP GEOLOCATION EXPLORER")
        in_layout = QHBoxLayout()
        self.dns_input = QLineEdit("cloudflare.com")
        self.dns_input.setPlaceholderText("Enter domain or IP...")
        btn_resolve = NeonButton("⚡ DISCOVER INFO", variant="green")
        btn_resolve.clicked.connect(self._run_dns_lookup)
        in_layout.addWidget(QLabel("Host / IP:"))
        in_layout.addWidget(self.dns_input)
        in_layout.addWidget(btn_resolve)
        in_card.addLayout(in_layout)
        layout.addWidget(in_card)

        # Stats Row
        geo_row = QHBoxLayout()
        self.stat_ip = StatCard("Resolved IP", "-", color=THEME['accent_cyan'])
        self.stat_country = StatCard("Country / City", "-", color=THEME['accent_green'])
        self.stat_isp = StatCard("ISP / Org", "-", color=THEME['accent_purple'])
        self.stat_asn = StatCard("ASN Number", "-", color=THEME['accent_amber'])
        geo_row.addWidget(self.stat_ip)
        geo_row.addWidget(self.stat_country)
        geo_row.addWidget(self.stat_isp)
        geo_row.addWidget(self.stat_asn)
        layout.addLayout(geo_row)

        # DNS Records
        dns_card = FuturisticCard("RESOLVED DNS RECORDS")
        self.dns_table = QTableWidget()
        self.dns_table.setColumnCount(2)
        self.dns_table.setHorizontalHeaderLabels(["Record Type", "Resolved Value"])
        self.dns_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        dns_card.addWidget(self.dns_table)
        layout.addWidget(dns_card)

        return widget

    def _run_dns_lookup(self):
        query = self.dns_input.text().strip()
        if not query:
            return

        # 1. Geo & IP info
        geo = OSINTEngine.get_ip_info(query)
        if geo.get("success"):
            self.stat_ip.set_value(geo.get("ip", "-"))
            self.stat_country.set_value(f"{geo.get('country')}, {geo.get('city')}")
            self.stat_isp.set_value(geo.get("isp", "-")[:20])
            self.stat_asn.set_value(geo.get("asn", "-")[:20])

        # 2. DNS
        dns_res = OSINTEngine.resolve_dns(query)
        records = dns_res.get("records", {})
        
        rows = []
        for r_type, vals in records.items():
            for v in vals:
                rows.append((r_type, str(v)))

        self.dns_table.setRowCount(len(rows))
        for i, (rt, val) in enumerate(rows):
            self.dns_table.setItem(i, 0, QTableWidgetItem(rt))
            self.dns_table.setItem(i, 1, QTableWidgetItem(val))
