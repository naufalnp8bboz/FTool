import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
ICON_PATH = os.path.join(ASSETS_DIR, "app_icon.ico")

# App Details
APP_NAME = "FTool"
APP_SUBTITLE = "Futuristic All-in-One Dev & Machine Learning Studio"
APP_VERSION = "1.0.0"
AUTHOR = "FTech"

# Cyber & Futuristic Theme Palette
THEME = {
    "bg_dark": "#090d16",
    "bg_card": "#101626",
    "bg_card_hover": "#162035",
    "bg_input": "#0d1322",
    "border_subtle": "#1d2942",
    "border_glow": "#00e5ff",
    "border_glow_purple": "#7c4dff",
    "accent_cyan": "#00e5ff",
    "accent_cyan_glow": "rgba(0, 229, 255, 0.25)",
    "accent_purple": "#7c4dff",
    "accent_purple_glow": "rgba(124, 77, 255, 0.25)",
    "accent_green": "#00e676",
    "accent_amber": "#ffb300",
    "accent_red": "#ff5252",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
}

# Master Futuristic QSS Stylesheet
GLOBAL_QSS = f"""
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
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {THEME['border_subtle']};
    min-height: 25px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: {THEME['accent_cyan']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background: {THEME['bg_dark']};
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {THEME['border_subtle']};
    min-width: 25px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {THEME['accent_cyan']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Inputs & Text Edits */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {THEME['bg_input']};
    border: 1px solid {THEME['border_subtle']};
    border-radius: 6px;
    padding: 8px 12px;
    color: {THEME['text_primary']};
    selection-background-color: {THEME['accent_cyan']};
    selection-color: #000000;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {THEME['accent_cyan']};
    background-color: #111a2e;
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
    selection-background-color: {THEME['accent_purple']};
    selection-color: white;
    color: {THEME['text_primary']};
    padding: 4px;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {THEME['border_subtle']};
    background-color: {THEME['bg_card']};
    border-radius: 8px;
    padding: 6px;
}}
QTabBar::tab {{
    background: {THEME['bg_input']};
    border: 1px solid {THEME['border_subtle']};
    padding: 8px 18px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: {THEME['text_secondary']};
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background: {THEME['bg_card']};
    color: {THEME['accent_cyan']};
    border-bottom: 2px solid {THEME['accent_cyan']};
}}
QTabBar::tab:hover:!selected {{
    background: {THEME['bg_card_hover']};
    color: {THEME['text_primary']};
}}

/* Push Buttons */
QPushButton {{
    background-color: {THEME['bg_card']};
    border: 1px solid {THEME['border_subtle']};
    border-radius: 6px;
    padding: 8px 16px;
    color: {THEME['text_primary']};
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {THEME['bg_card_hover']};
    border-color: {THEME['accent_cyan']};
    color: {THEME['accent_cyan']};
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
    border-radius: 6px;
    gridline-color: #182236;
    color: {THEME['text_primary']};
    selection-background-color: rgba(0, 229, 255, 0.2);
    selection-color: {THEME['text_primary']};
}}
QHeaderView::section {{
    background-color: {THEME['bg_input']};
    color: {THEME['text_secondary']};
    padding: 6px;
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
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {THEME['accent_purple']}, stop:1 {THEME['accent_cyan']});
    border-radius: 3px;
}}
"""
