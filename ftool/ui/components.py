import math
import re
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QRect, QSize, QTimer, QPointF
from PyQt6.QtGui import (
    QColor, QPainter, QTextFormat, QFont, QSyntaxHighlighter,
    QTextCharFormat, QPen, QBrush, QLinearGradient
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ftool.config import THEME

class AnimatedWaveformWidget(QWidget):
    """High-tech cyberpunk telemetry waveform monitor for the header bar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 32)
        self.phase = 0.0
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self._update_wave)
        self.timer.start()

    def _update_wave(self):
        self.phase += 0.15
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        mid_y = h / 2.0

        # Draw subtle grid
        pen_grid = QPen(QColor(THEME['border_subtle']))
        pen_grid.setWidth(1)
        painter.setPen(pen_grid)
        painter.drawLine(0, int(mid_y), w, int(mid_y))

        # Draw animated sine telemetry wave
        pen_wave = QPen(QColor(THEME['accent_cyan']))
        pen_wave.setWidth(2)
        painter.setPen(pen_wave)

        prev_x = 0
        prev_y = mid_y
        for x in range(0, w, 3):
            # Combined harmonics
            rad = (x / 14.0) + self.phase
            y = mid_y + math.sin(rad) * 9.0 + math.cos(rad * 1.7) * 3.0
            painter.drawLine(int(prev_x), int(prev_y), int(x), int(y))
            prev_x = x
            prev_y = y


class NeuralNetworkGraphWidget(QWidget):
    """Interactive visualizer for multi-layer perceptron topology and synapse weights."""
    def __init__(self, layer_sizes=(4, 6, 3), parent=None):
        super().__init__(parent)
        self.layer_sizes = layer_sizes
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_layers(self, layer_sizes):
        self.layer_sizes = layer_sizes
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Background
        painter.fillRect(0, 0, w, h, QColor(THEME['bg_dark']))

        if not self.layer_sizes:
            return

        num_layers = len(self.layer_sizes)
        x_spacing = (w - 80) / max(1, num_layers - 1)

        # Calculate node positions
        layer_positions = []
        for l_idx, count in enumerate(self.layer_sizes):
            x = 40 + l_idx * x_spacing
            y_spacing = (h - 60) / max(1, count)
            nodes = []
            for n_idx in range(count):
                y = 30 + (n_idx + 0.5) * y_spacing
                nodes.append((x, y))
            layer_positions.append(nodes)

        # Draw Synapse Lines between adjacent layers
        for l_idx in range(num_layers - 1):
            left_nodes = layer_positions[l_idx]
            right_nodes = layer_positions[l_idx + 1]

            for i, (x1, y1) in enumerate(left_nodes):
                for j, (x2, y2) in enumerate(right_nodes):
                    # Deterministic simulated weight color
                    weight_val = math.sin(i * 1.5 + j * 2.3 + l_idx)
                    if weight_val > 0:
                        color = QColor(0, 229, 255, int(abs(weight_val) * 140 + 40)) # Cyan
                    else:
                        color = QColor(124, 77, 255, int(abs(weight_val) * 140 + 40)) # Purple

                    pen = QPen(color)
                    pen.setWidthF(max(1.0, abs(weight_val) * 2.2))
                    painter.setPen(pen)
                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Draw Nodes
        node_radius = 12
        for l_idx, nodes in enumerate(layer_positions):
            for n_idx, (x, y) in enumerate(nodes):
                # Node Glow
                glow_color = QColor(0, 229, 255, 60) if l_idx == 0 else (
                    QColor(0, 230, 118, 90) if l_idx == num_layers - 1 else QColor(124, 77, 255, 70)
                )
                painter.setBrush(QBrush(glow_color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(x, y), node_radius + 4, node_radius + 4)

                # Node Body
                body_color = QColor(THEME['bg_card'])
                border_color = QColor(THEME['accent_cyan']) if l_idx == 0 else (
                    QColor(THEME['accent_green']) if l_idx == num_layers - 1 else QColor(THEME['accent_purple'])
                )
                painter.setBrush(QBrush(body_color))
                painter.setPen(QPen(border_color, 2))
                painter.drawEllipse(QPointF(x, y), node_radius, node_radius)

                # Text index inside node
                painter.setPen(QColor(THEME['text_primary']))
                font = QFont("Consolas", 8, QFont.Weight.Bold)
                painter.setFont(font)
                label = f"x{n_idx+1}" if l_idx == 0 else (f"y{n_idx+1}" if l_idx == num_layers - 1 else f"h{n_idx+1}")
                painter.drawText(QRect(int(x - 12), int(y - 8), 24, 16), Qt.AlignmentFlag.AlignCenter, label)

        # Layer labels at bottom
        painter.setPen(QColor(THEME['text_secondary']))
        font_lbl = QFont("Segoe UI", 9, QFont.Weight.Bold)
        painter.setFont(font_lbl)
        for l_idx, nodes in enumerate(layer_positions):
            x = nodes[0][0]
            name = "Input Layer" if l_idx == 0 else ("Output Layer" if l_idx == num_layers - 1 else f"Hidden Layer {l_idx}")
            painter.drawText(QRect(int(x - 60), h - 22, 120, 20), Qt.AlignmentFlag.AlignCenter, name)


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
        self.lbl_value.setStyleSheet(f"font-size: 19px; font-weight: 700; color: {color}; border: none;")
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
    def __init__(self, width=5, height=3.5, dpi=100, parent=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=THEME['bg_card'])
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()
