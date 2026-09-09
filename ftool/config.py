import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
ICON_PATH = os.path.join(ASSETS_DIR, "app_icon.ico")

# App Details
APP_NAME = "FTool"
APP_SUBTITLE = "Next-Gen Dev, OSINT & Machine Learning Suite"
APP_VERSION = "2.0.0"
AUTHOR = "FTech"

# Cyber & Futuristic Theme Palette
THEMES = {
    "Cyan": {
        "accent": "#00e5ff",
        "accent_glow": "rgba(0, 229, 255, 0.25)",
        "accent_secondary": "#7c4dff",
    },
    "Violet": {
        "accent": "#c084fc",
        "accent_glow": "rgba(192, 132, 252, 0.25)",
        "accent_secondary": "#06b6d4",
    },
    "Matrix": {
        "accent": "#00e676",
        "accent_glow": "rgba(0, 230, 118, 0.25)",
        "accent_secondary": "#00e5ff",
    },
    "Solar": {
        "accent": "#ffb300",
        "accent_glow": "rgba(255, 179, 0, 0.25)",
        "accent_secondary": "#ff5252",
    }
}

CURRENT_THEME = "Cyan"

THEME = {
    "bg_dark": "#070a12",
    "bg_surface": "#0c111d",
    "bg_card": "#101726",
    "bg_card_hover": "#162035",
    "bg_input": "#0b101c",
    "border_subtle": "#1c263c",
    "border_glow": "#00e5ff",
    "border_glow_purple": "#7c4dff",
    "accent_cyan": "#00e5ff",
    "accent_cyan_glow": "rgba(0, 229, 255, 0.25)",
    "accent_purple": "#7c4dff",
    "accent_purple_glow": "rgba(124, 77, 255, 0.25)",
    "accent_green": "#00e676",
    "accent_amber": "#ffb300",
    "accent_red": "#ff5252",
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_muted": "#475569",
}

def get_qss(accent_color: str = THEME['accent_cyan']) -> str:
    return f"""
QMainWindow, QDialog {{
    background-color: {THEME['bg_dark']};
    color: {THEME['text_primary']};
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
}}

QWidget {{
    background-color: transparent;
    color: {THEME['text_primary']};
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}}

/* Custom Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: {THEME['bg_dark']};
    width: 7px;
    margin: 0px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {THEME['border_subtle']};
    min-height: 25px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical:hover {{
    background: {accent_color};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background: {THEME['bg_dark']};
    height: 7px;
    margin: 0px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {THEME['border_subtle']};
    min-width: 25px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {accent_color};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Inputs & Text Edits */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {THEME['bg_input']};
    border: 1px solid {THEME['border_subtle']};
    border-radius: 7px;
    padding: 8px 12px;
    color: {THEME['text_primary']};
    selection-background-color: {accent_color};
    selection-color: #000000;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {accent_color};
    background-color: #0f1728;
}}

/* ComboBox */
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid {THEME['border_subtle']};
}}
QComboBox QAbstractItemView {{
    background-color: {THEME['bg_card']};
    border: 1px solid {THEME['border_subtle']};
    selection-background-color: {accent_color};
    selection-color: #000000;
    color: {THEME['text_primary']};
    padding: 6px;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {THEME['border_subtle']};
    background-color: {THEME['bg_card']};
    border-radius: 8px;
    padding: 8px;
}}
QTabBar::tab {{
    background: {THEME['bg_input']};
    border: 1px solid {THEME['border_subtle']};
    padding: 8px 18px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: {THEME['text_secondary']};
    font-weight: 600;
}}
QTabBar::tab:selected {{
    background: {THEME['bg_card']};
    color: {accent_color};
    border-bottom: 2px solid {accent_color};
}}
QTabBar::tab:hover:!selected {{
    background: {THEME['bg_card_hover']};
    color: {THEME['text_primary']};
}}

/* Push Buttons */
QPushButton {{
    background-color: {THEME['bg_card']};
    border: 1px solid {THEME['border_subtle']};
    border-radius: 7px;
    padding: 8px 16px;
    color: {THEME['text_primary']};
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {THEME['bg_card_hover']};
    border-color: {accent_color};
    color: {accent_color};
}}
QPushButton:pressed {{
    background-color: #1a2742;
}}
QPushButton:disabled {{
    background-color: #0b0f19;
    border-color: #172033;
    color: {THEME['text_muted']};
}}

/* Tables */
QTableWidget, QTableView {{
    background-color: {THEME['bg_card']};
    border: 1px solid {THEME['border_subtle']};
    border-radius: 7px;
    gridline-color: #151f33;
    color: {THEME['text_primary']};
    selection-background-color: rgba(0, 229, 255, 0.15);
    selection-color: {THEME['text_primary']};
}}
QHeaderView::section {{
    background-color: {THEME['bg_input']};
    color: {THEME['text_secondary']};
    padding: 7px;
    border: 1px solid {THEME['border_subtle']};
    font-weight: 600;
}}

/* Progress Bar */
QProgressBar {{
    background-color: {THEME['bg_input']};
    border: 1px solid {THEME['border_subtle']};
    border-radius: 4px;
    text-align: center;
    color: white;
    font-size: 11px;
    height: 14px;
}}
QProgressBar::chunk {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {THEME['accent_purple']}, stop:1 {accent_color});
    border-radius: 3px;
}}
"""

GLOBAL_QSS = get_qss(THEME['accent_cyan'])
