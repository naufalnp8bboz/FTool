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

        # Scroll Area for responsiveness
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
        title = QLabel(f"⚡ WELCOME TO {APP_NAME.upper()}")
        title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: 1px;")
        sub = QLabel(f"{APP_SUBTITLE} — Effortless for beginners, powerful for engineers.")
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
        self.stat_engine = StatCard("Engine Status", "ONLINE", unit="Ready", color=THEME['accent_cyan'])
        
        stats_layout.addWidget(self.stat_cpu)
        stats_layout.addWidget(self.stat_ram)
        stats_layout.addWidget(self.stat_disk)
        stats_layout.addWidget(self.stat_engine)
        layout.addLayout(stats_layout)

        # Quick Access Grid
        grid_card = FuturisticCard("QUICK LAUNCH WORKSPACES")
        grid = QGridLayout()
        grid.setSpacing(14)

        modules = [
            ("🤖 Machine Learning Studio", "Train classifiers, regressors, auto-EDA, visual confusion matrix, code exporter.", 1, "cyan"),
            ("💻 Code Studio & Runner", "Write, format, inspect AST, and execute Python code with sub-millisecond benchmarking.", 2, "purple"),
            ("👁️ Computer Vision Sandbox", "Interactive image processing: Canny edge detection, blur, colormaps, contours.", 3, "green"),
            ("📝 NLP & Sentiment Lab", "Real-time polarity, readability score, keyword extraction, and cosine similarity.", 4, "cyan"),
            ("🛠️ Dev Utilities & API Tester", "Regex tester, HTTP/Webhook tester, Base64/Hash/JWT conversion tools.", 5, "purple"),
            ("⚡ Guided Command Runner", "Automate complex terminal commands with one-click beginner-friendly presets.", 6, "green"),
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
            
            btn = NeonButton("OPEN MODULE →", variant=variant)
            btn.clicked.connect(lambda _, idx=tab_idx: self._open_tab(idx))
            
            b_layout.addWidget(lbl_name)
            b_layout.addWidget(lbl_d)
            b_layout.addSpacing(6)
            b_layout.addWidget(btn)
            grid.addWidget(box, row, col)

        grid_card.addLayout(grid)
        layout.addWidget(grid_card)

        # Beginner Tips Card
        tips_card = FuturisticCard("PRO TIPS FOR BEGINNERS")
        tips_layout = QVBoxLayout()
        tips = [
            "• **Zero Coding Machine Learning**: Click 'ML Studio', select 'Iris' or 'Customer Churn' sample, and hit 'Train Model' to see instant accuracy and visual confusion matrix!",
            "• **Generated Code**: Click 'Generate Python Code' in the ML Studio to copy ready-to-run code for your own projects.",
            "• **Regex & API Sandbox**: Use the 'Dev Utilities' tab to inspect JSON payloads, format code, and test regex matches with real-time feedback."
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
