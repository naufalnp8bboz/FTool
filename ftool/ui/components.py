import re
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QColor, QPainter, QTextFormat, QFont, QSyntaxHighlighter, QTextCharFormat
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ftool.config import THEME

class FuturisticCard(QFrame):
    """Sleek minimalist dark card with subtle glowing borders."""
    def __init__(self, title: str = "", parent=None, accent_color=None):
        super().__init__(parent)
        self.accent = accent_color or THEME['border_subtle']
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME['bg_card']};
                border: 1px solid {self.accent};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(10)

        if title:
            title_lbl = QLabel(title.upper())
            title_lbl.setStyleSheet(f"""
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1.5px;
                color: {THEME['accent_cyan']};
                border: none;
                padding: 0;
            """)
            self.main_layout.addWidget(title_lbl)

    def addWidget(self, widget):
        self.main_layout.addWidget(widget)

    def addLayout(self, layout):
        self.main_layout.addLayout(layout)


class NeonButton(QPushButton):
    """High-tech button with glowing neon accents."""
    def __init__(self, text: str, variant: str = "cyan", parent=None):
        super().__init__(text, parent)
        color = THEME['accent_cyan'] if variant == "cyan" else (
            THEME['accent_purple'] if variant == "purple" else THEME['accent_green']
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['bg_card']};
                border: 1px solid {color};
                border-radius: 6px;
                padding: 6px 16px;
                color: {color};
                font-weight: 700;
                font-size: 12px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: #000000;
            }}
            QPushButton:pressed {{
                background-color: #090d16;
                color: {color};
            }}
            QPushButton:disabled {{
                border-color: #2a3449;
                color: #52607d;
                background-color: {THEME['bg_card']};
            }}
        """)


class StatCard(QFrame):
    """Displays a key metric (e.g. Accuracy, Latency, Samples)."""
    def __init__(self, label: str, value: str = "-", unit: str = "", color: str = THEME['accent_cyan'], parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border_subtle']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        self.lbl_title = QLabel(label.upper())
        self.lbl_title.setStyleSheet(f"font-size: 10px; color: {THEME['text_muted']}; font-weight: 600; border: none;")

        val_layout = QHBoxLayout()
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {color}; border: none;")
        val_layout.addWidget(self.lbl_value)

        if unit:
            lbl_unit = QLabel(unit)
            lbl_unit.setStyleSheet(f"font-size: 11px; color: {THEME['text_secondary']}; border: none; margin-bottom: 2px;")
            val_layout.addWidget(lbl_unit, alignment=Qt.AlignmentFlag.AlignBottom)
        val_layout.addStretch()

        layout.addWidget(self.lbl_title)
        layout.addLayout(val_layout)

    def set_value(self, val: str):
        self.lbl_value.setText(val)


class PythonHighlighter(QSyntaxHighlighter):
    """Lightweight Python syntax highlighter."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(THEME['accent_cyan']))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            r'\bdef\b', r'\bclass\b', r'\breturn\b', r'\bimport\b', r'\bfrom\b',
            r'\bas\b', r'\bif\b', r'\belif\b', r'\belse\b', r'\bwhile\b',
            r'\bfor\b', r'\bin\b', r'\btry\b', r'\bexcept\b', r'\bfinally\b',
            r'\bwith\b', r'\bpass\b', r'\blambda\b', r'\byield\b', r'\bTrue\b',
            r'\bFalse\b', r'\bNone\b'
        ]
        for pattern in keywords:
            self.highlighting_rules.append((re.compile(pattern), keyword_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor(THEME['accent_green']))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(THEME['text_muted']))
        self.highlighting_rules.append((re.compile(r'#[^\n]*'), comment_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(THEME['accent_purple']))
        self.highlighting_rules.append((re.compile(r'\b[0-9]+(\.[0-9]+)?\b'), number_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)


class FuturisticCodeEditor(QPlainTextEdit):
    """Futuristic code editor with line numbers and Python syntax coloring."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {THEME['bg_input']};
                border: 1px solid {THEME['border_subtle']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 4px;
            }}
            QPlainTextEdit:focus {{
                border-color: {THEME['accent_cyan']};
            }}
        """)
        self.highlighter = PythonHighlighter(self.document())

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 14 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(THEME['bg_dark']))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(THEME['text_muted']))
                painter.drawText(0, int(top), self.line_number_area.width() - 6, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1


class DarkPlotCanvas(FigureCanvas):
    """Embeddable Matplotlib canvas with dark futuristic theme."""
    def __init__(self, width=5, height=4, dpi=100, parent=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=THEME['bg_card'])
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()
