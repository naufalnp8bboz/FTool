import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QProgressBar
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QFont
from ftool.config import LOGO_PATH, THEME, APP_NAME, APP_SUBTITLE

class FuturisticSplashScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(540, 560)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Background container frame
        container = QWidget(self)
        container.setFixedSize(500, 520)
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 2px solid {THEME['accent_cyan']};
                border-radius: 16px;
            }}
        """)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(30, 40, 30, 30)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.setSpacing(16)

        # Logo Image
        self.lbl_logo = QLabel()
        self.lbl_logo.setStyleSheet("border: none; background: transparent;")
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if os.path.exists(LOGO_PATH):
            pixmap = QPixmap(LOGO_PATH).scaled(
                260, 260,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_logo.setPixmap(pixmap)
        else:
            self.lbl_logo.setText("[ FTech ]")
            self.lbl_logo.setStyleSheet(f"color: {THEME['accent_cyan']}; font-size: 32px; font-weight: bold; border: none;")

        # Title & Subtitle
        self.lbl_title = QLabel(APP_NAME)
        self.lbl_title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 4px;
            border: none;
            background: transparent;
        """)
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_sub = QLabel("FTech • Intelligent Dev & Machine Learning Studio")
        self.lbl_sub.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {THEME['accent_cyan']};
            letter-spacing: 1.5px;
            border: none;
            background: transparent;
        """)
        self.lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Status text
        self.lbl_status = QLabel("Initializing cores...")
        self.lbl_status.setStyleSheet(f"font-size: 11px; color: {THEME['text_muted']}; border: none; background: transparent;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        c_layout.addSpacing(10)
        c_layout.addWidget(self.progress)
        c_layout.addWidget(self.lbl_status)

        layout.addWidget(container)

        # Opacity effect for smooth fading
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        # Fade in animation (0 to 600ms)
        self.anim_fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_fade_in.setDuration(600)
        self.anim_fade_in.setStartValue(0.0)
        self.anim_fade_in.setEndValue(1.0)
        self.anim_fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Fade out animation (last 500ms of 3 seconds)
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

    def start_splash(self):
        self.show()
        self.anim_fade_in.start()
        self.timer.start()

    def _tick(self):
        self.current_time_ms += 30
        pct = min(100, int((self.current_time_ms / self.total_duration_ms) * 100))
        self.progress.setValue(pct)

        if pct < 30:
            self.lbl_status.setText("Loading AI & Scikit Engines...")
        elif pct < 70:
            self.lbl_status.setText("Configuring Code Studio & Vision Core...")
        else:
            self.lbl_status.setText("Ready. Launching FTool...")

        if self.current_time_ms >= (self.total_duration_ms - 500) and not self.anim_fade_out.state() == QPropertyAnimation.State.Running:
            self.anim_fade_out.start()

        if self.current_time_ms >= self.total_duration_ms:
            self.timer.stop()

    def _on_splash_done(self):
        self.close()
        self.finished.emit()

    def mousePressEvent(self, event):
        # Allow instant skip by clicking
        self.timer.stop()
        self.close()
        self.finished.emit()
