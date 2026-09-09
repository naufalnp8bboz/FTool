from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from ftool.config import THEME, APP_NAME, APP_SUBTITLE
from ftool.ui.components import FuturisticCard, NeonButton, StatCard
from ftool.core.utils import SystemMonitor

class DashboardTab(QWidget):
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Welcome Banner
        banner = FuturisticCard(accent_color=THEME['accent_cyan'])
        banner_layout = QVBoxLayout()
        title = QLabel(f"⚡ {APP_NAME.upper()} — NEXT-GEN WORKSPACE")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: 1px;")
        sub = QLabel(f"{APP_SUBTITLE} — Bridging deep engineering intelligence with effortless beginner design.")
        sub.setStyleSheet(f"font-size: 13px; color: {THEME['text_secondary']};")
        banner_layout.addWidget(title)
        banner_layout.addWidget(sub)
        banner.addLayout(banner_layout)
        layout.addWidget(banner)

        # System Monitor Stats Grid
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        self.stat_cpu = StatCard("CPU Load", "0%", unit="Total", color=THEME['accent_cyan'])
        self.stat_ram = StatCard("RAM Usage", "0%", unit="GB", color=THEME['accent_purple'])
        self.stat_disk = StatCard("System Disk", "0%", unit="Used", color=THEME['accent_green'])
        self.stat_engine = StatCard("Neural Cores", "ACTIVE", unit="v2.0", color=THEME['accent_cyan'])
        
        stats_layout.addWidget(self.stat_cpu)
        stats_layout.addWidget(self.stat_ram)
        stats_layout.addWidget(self.stat_disk)
        stats_layout.addWidget(self.stat_engine)
        layout.addLayout(stats_layout)

        # Quick Access Grid (All modules)
        grid_card = FuturisticCard("ALL-IN-ONE STUDIOS & WORKSPACES")
        grid = QGridLayout()
        grid.setSpacing(12)

        modules = [
            ("🛡️ Defensive OSINT & Recon", "Passive username scout, SSL cert analyzer, HTTP security posture grading (A-F), and DNS explorer.", 1, "cyan"),
            ("🧠 ML & Neural Net Studio", "Train Neural Networks (MLP), Random Forest, SVM; interactive neuron topology visualizer & loss curve.", 2, "purple"),
            ("🤖 AI Prompt & LLM Studio", "Connect local Ollama or cloud models, prompt engineering templates for code fix, SQL, and regex.", 3, "green"),
            ("💻 Code Studio & Runner", "Sub-millisecond Python script runner, AST code structure parser, and interactive console.", 4, "cyan"),
            ("🎯 Vision & Cyber Face HUD", "OpenCV Face & Eye targeting reticles, real-time live webcam neural filter, and colormaps.", 5, "purple"),
            ("📝 NLP & Sentiment Lab", "Polarity sentiment scoring, readability grade (Flesch), keyword extraction, and cosine similarity.", 6, "green"),
            ("🛠️ Dev Utilities & API Tester", "Regex sandbox with capture groups, HTTP/Webhook requester, Base64/Hash/JWT Swiss-Army tools.", 7, "cyan"),
            ("⚡ Guided Workflow Runner", "Automate complex CLI tasks (port scanner, Git status, Python diagnostic) with zero terminal fuss.", 8, "purple"),
        ]

        for i, (mod_title, mod_desc, tab_idx, variant) in enumerate(modules):
            row = i // 2
            col = i % 2
            box = QFrame()
            box.setStyleSheet(f"""
                QFrame {{
                    background-color: {THEME['bg_input']};
                    border: 1px solid {THEME['border_subtle']};
                    border-radius: 8px;
                    padding: 10px;
                }}
                QFrame:hover {{
                    border-color: {THEME['accent_cyan']};
                }}
            """)
            b_layout = QVBoxLayout(box)
            b_layout.setSpacing(6)
            lbl_name = QLabel(mod_title)
            lbl_name.setStyleSheet("font-size: 14px; font-weight: 700; color: #ffffff;")
            lbl_d = QLabel(mod_desc)
            lbl_d.setWordWrap(True)
            lbl_d.setStyleSheet(f"font-size: 11px; color: {THEME['text_secondary']};")
            
            btn = NeonButton("LAUNCH MODULE →", variant=variant)
            btn.clicked.connect(lambda _, idx=tab_idx: self._open_tab(idx))
            
            b_layout.addWidget(lbl_name)
            b_layout.addWidget(lbl_d)
            b_layout.addSpacing(6)
            b_layout.addWidget(btn)
            grid.addWidget(box, row, col)

        grid_card.addLayout(grid)
        layout.addWidget(grid_card)

        # Beginner & Pro Tips Card
        tips_card = FuturisticCard("INTELLIGENT WORKFLOW CHEATSHEET")
        tips_layout = QVBoxLayout()
        tips = [
            "• **Defensive OSINT**: Use 'OSINT & Recon' to audit website security headers and discover missing defenses like CSP or HSTS.",
            "• **Neural Network Topology**: In 'ML Studio', train the 'Neural Network (MLP)' model to see the interactive synaptic node graph update in real-time.",
            "• **Cyber Face Detection**: In 'Vision & Face HUD', select 'Cyber Face & Eye HUD' or toggle 'Live Webcam' for instant holographic targeting.",
            "• **Local AI Models**: Run `ollama run llama3` on your PC, then click 'Detect Ollama' in 'AI Prompt Studio' for private, local LLM generation."
        ]
        for tip in tips:
            lbl_tip = QLabel(tip)
            lbl_tip.setTextFormat(Qt.TextFormat.MarkdownText)
            lbl_tip.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 12px; margin-bottom: 4px;")
            tips_layout.addWidget(lbl_tip)
        tips_card.addLayout(tips_layout)
        layout.addWidget(tips_card)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Refresh stats timer
        self.stats_timer = QTimer(self)
        self.stats_timer.setInterval(2000)
        self.stats_timer.timeout.connect(self._refresh_stats)
        self.stats_timer.start()
        self._refresh_stats()

    def _open_tab(self, index: int):
        if self.parent_window:
            self.parent_window.switch_tab(index)

    def _refresh_stats(self):
        stats = SystemMonitor.get_system_stats()
        self.stat_cpu.set_value(f"{stats['cpu_percent']}%")
        self.stat_ram.set_value(f"{stats['ram_percent']}%")
        self.stat_disk.set_value(f"{stats['disk_percent']}%")
