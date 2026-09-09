import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QFrame, QButtonGroup
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from ftool.config import (
    APP_NAME, APP_SUBTITLE, APP_VERSION, AUTHOR, LOGO_PATH, ICON_PATH, THEME, GLOBAL_QSS
)
from ftool.ui.tabs.tab_dashboard import DashboardTab
from ftool.ui.tabs.tab_ml_studio import MLStudioTab
from ftool.ui.tabs.tab_code_studio import CodeStudioTab
from ftool.ui.tabs.tab_cv_sandbox import CVSandboxTab
from ftool.ui.tabs.tab_nlp_tools import NLPToolsTab
from ftool.ui.tabs.tab_dev_tools import DevToolsTab
from ftool.ui.tabs.tab_runner import RunnerTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — {APP_SUBTITLE}")
        self.resize(1280, 820)
        self.setMinimumSize(1024, 700)

        # Set Icon
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        elif os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))

        # Apply Global QSS
        self.setStyleSheet(GLOBAL_QSS)

        # Central Widget & Root Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        # 2. Right Content Area (Top Bar + QStackedWidget)
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar
        top_bar = self._build_top_bar()
        content_layout.addWidget(top_bar)

        # Stacked Widget for Tabs
        self.stacked_widget = QStackedWidget()
        self.dashboard_tab = DashboardTab(parent_window=self)
        self.ml_tab = MLStudioTab()
        self.code_tab = CodeStudioTab()
        self.cv_tab = CVSandboxTab()
        self.nlp_tab = NLPToolsTab()
        self.dev_tab = DevToolsTab()
        self.runner_tab = RunnerTab()

        self.stacked_widget.addWidget(self.dashboard_tab)
        self.stacked_widget.addWidget(self.ml_tab)
        self.stacked_widget.addWidget(self.code_tab)
        self.stacked_widget.addWidget(self.cv_tab)
        self.stacked_widget.addWidget(self.nlp_tab)
        self.stacked_widget.addWidget(self.dev_tab)
        self.stacked_widget.addWidget(self.runner_tab)

        content_layout.addWidget(self.stacked_widget)
        root_layout.addWidget(content_area)

        # Select Dashboard by default
        self.nav_buttons[0].setChecked(True)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME['bg_dark']};
                border-right: 1px solid {THEME['border_subtle']};
            }}
        """)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 20, 14, 16)
        layout.setSpacing(6)

        # Brand header with Logo
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)

        if os.path.exists(LOGO_PATH):
            logo_lbl = QLabel()
            pix = QPixmap(LOGO_PATH).scaled(34, 34, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pix)
            logo_lbl.setStyleSheet("border: none; background: transparent;")
            brand_layout.addWidget(logo_lbl)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        lbl_brand = QLabel(APP_NAME)
        lbl_brand.setStyleSheet("font-size: 16px; font-weight: 800; color: #ffffff; letter-spacing: 2px; border: none;")
        lbl_credit = QLabel(f"by {AUTHOR}")
        lbl_credit.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {THEME['accent_cyan']}; border: none;")
        title_box.addWidget(lbl_brand)
        title_box.addWidget(lbl_credit)

        brand_layout.addLayout(title_box)
        brand_layout.addStretch()
        layout.addLayout(brand_layout)

        layout.addSpacing(20)

        # Nav Buttons
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = []

        nav_items = [
            ("📊  Dashboard", 0),
            ("🤖  ML Studio", 1),
            ("💻  Code Studio", 2),
            ("👁️  Vision Sandbox", 3),
            ("📝  NLP & Sentiment", 4),
            ("🛠️  Dev Utilities", 5),
            ("⚡  Guided Runner", 6),
        ]

        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    padding-left: 14px;
                    text-align: left;
                    color: {THEME['text_secondary']};
                    font-size: 13px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {THEME['bg_card']};
                    color: #ffffff;
                }}
                QPushButton:checked {{
                    background-color: {THEME['bg_card_hover']};
                    color: {THEME['accent_cyan']};
                    border-left: 3px solid {THEME['accent_cyan']};
                }}
            """)
            btn.clicked.connect(lambda _, index=idx: self.switch_tab(index))
            self.nav_group.addButton(btn, idx)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Footer info
        footer = QLabel(f"FTool v{APP_VERSION} Open Source\nReady for Developers")
        footer.setStyleSheet(f"font-size: 10px; color: {THEME['text_muted']}; border: none; padding: 4px;")
        layout.addWidget(footer)

        return sidebar

    def _build_top_bar(self) -> QWidget:
        top_bar = QFrame()
        top_bar.setFixedHeight(50)
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME['bg_dark']};
                border-bottom: 1px solid {THEME['border_subtle']};
            }}
        """)
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(20, 0, 20, 0)

        self.lbl_current_tab = QLabel("DASHBOARD OVERVIEW")
        self.lbl_current_tab.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; letter-spacing: 1px; border: none;")
        layout.addWidget(self.lbl_current_tab)

        layout.addStretch()

        # System Status Pill
        lbl_status = QLabel("● SYSTEM READY")
        lbl_status.setStyleSheet(f"""
            color: {THEME['accent_green']};
            font-size: 11px;
            font-weight: 700;
            background-color: rgba(0, 230, 118, 0.1);
            border: 1px solid rgba(0, 230, 118, 0.3);
            border-radius: 12px;
            padding: 4px 12px;
        """)
        layout.addWidget(lbl_status)

        return top_bar

    def switch_tab(self, index: int):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        tab_names = [
            "DASHBOARD OVERVIEW",
            "MACHINE LEARNING STUDIO",
            "PYTHON CODE STUDIO & AST INSPECTOR",
            "COMPUTER VISION FILTER SANDBOX",
            "NLP, SENTIMENT & SIMILARITY LAB",
            "DEVELOPER UTILITIES & API TESTER",
            "GUIDED WORKFLOW RUNNER"
        ]
        if index < len(tab_names):
            self.lbl_current_tab.setText(tab_names[index])
