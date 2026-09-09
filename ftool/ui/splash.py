import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QProgressBar, QTextEdit
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QFont
from ftool.config import LOGO_PATH, THEME, APP_NAME, APP_SUBTITLE

class FuturisticSplashScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(560, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Background container frame
        container = QWidget(self)
        container.setFixedSize(520, 560)
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 2px solid {THEME['accent_cyan']};
                border-radius: 18px;
            }}
        """)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(30, 36, 30, 26)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.setSpacing(12)

        # Logo Image
        self.lbl_logo = QLabel()
        self.lbl_logo.setStyleSheet("border: none; background: transparent;")
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if os.path.exists(LOGO_PATH):
            pixmap = QPixmap(LOGO_PATH).scaled(
                220, 220,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_logo.setPixmap(pixmap)
        else:
            self.lbl_logo.setText("[ FTech ]")
            self.lbl_logo.setStyleSheet(f"color: {THEME['accent_cyan']}; font-size: 32px; font-weight: bold; border: none;")

        # Title & Subtitle
        self.lbl_title = QLabel(APP_NAME)
        self.lbl_title.setStyleSheet("""
            font-size: 30px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 4px;
            border: none;
            background: transparent;
        """)
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_sub = QLabel("FTech • Next-Gen Dev, OSINT & Machine Learning Suite")
        self.lbl_sub.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {THEME['accent_cyan']};
            letter-spacing: 1.5px;
            border: none;
            background: transparent;
        """)
        self.lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Terminal Boot-Log Stream
        self.txt_boot = QTextEdit()
        self.txt_boot.setReadOnly(True)
        self.txt_boot.setFixedHeight(85)
        self.txt_boot.setFontFamily("Consolas")
        self.txt_boot.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0b0f19;
                border: 1px solid {THEME['border_subtle']};
                border-radius: 6px;
                color: #00e676;
                font-size: 10px;
                padding: 4px;
            }}
        """)
        self.txt_boot.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Futuristic Progress Bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: #121929;
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {THEME['accent_purple']}, stop:1 {THEME['accent_cyan']});
                border-radius: 3px;
            }}
        """)

        c_layout.addWidget(self.lbl_logo)
        c_layout.addWidget(self.lbl_title)
        c_layout.addWidget(self.lbl_sub)
        c_layout.addSpacing(6)
        c_layout.addWidget(self.progress)
        c_layout.addWidget(self.txt_boot)

        layout.addWidget(container)

        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        # Fade in animation
        self.anim_fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_fade_in.setDuration(500)
        self.anim_fade_in.setStartValue(0.0)
        self.anim_fade_in.setEndValue(1.0)
        self.anim_fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Fade out animation
        self.anim_fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_fade_out.setDuration(500)
        self.anim_fade_out.setStartValue(1.0)
        self.anim_fade_out.setEndValue(0.0)
        self.anim_fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim_fade_out.finished.connect(self._on_splash_done)

        # Progress ticker for 3 seconds total
        self.current_time_ms = 0
        self.total_duration_ms = 3000
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._tick)
        self.boot_steps_logged = set()

    def start_splash(self):
        self.show()
        self.anim_fade_in.start()
        self.timer.start()

    def _tick(self):
        self.current_time_ms += 30
        pct = min(100, int((self.current_time_ms / self.total_duration_ms) * 100))
        self.progress.setValue(pct)

        # High-tech boot sequencer logs
        if pct >= 10 and 10 not in self.boot_steps_logged:
            self.boot_steps_logged.add(10)
            self.txt_boot.append("[CORE_0] Initializing Neural & Tensor Subsystems... [OK]")
        elif pct >= 35 and 35 not in self.boot_steps_logged:
            self.boot_steps_logged.add(35)
            self.txt_boot.append("[VISION] OpenCV Haar Cascades & Filters Loaded... [OK]")
        elif pct >= 60 and 60 not in self.boot_steps_logged:
            self.boot_steps_logged.add(60)
            self.txt_boot.append("[OSINT] Defensive Security & DNS Core Online... [OK]")
        elif pct >= 85 and 85 not in self.boot_steps_logged:
            self.boot_steps_logged.add(85)
            self.txt_boot.append("[SYSTEM] FTech Core Activated. Launching FTool...")

        if self.current_time_ms >= (self.total_duration_ms - 500) and not self.anim_fade_out.state() == QPropertyAnimation.State.Running:
            self.anim_fade_out.start()

        if self.current_time_ms >= self.total_duration_ms:
            self.timer.stop()

    def _on_splash_done(self):
        self.close()
        self.finished.emit()

    def mousePressEvent(self, event):
        self.timer.stop()
        self.close()
        self.finished.emit()
