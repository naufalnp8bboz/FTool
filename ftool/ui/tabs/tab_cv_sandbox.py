import os
import cv2
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSlider, QFileDialog, QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from ftool.config import LOGO_PATH, THEME
from ftool.ui.components import FuturisticCard, NeonButton, StatCard
from ftool.core.cv_engine import CVEngine

class CVSandboxTab(QWidget):
    def __init__(self):
        super().__init__()
        self.cv_engine = CVEngine()
        self.cap = None
        self.webcam_timer = QTimer(self)
        self.webcam_timer.setInterval(33) # ~30 FPS
        self.webcam_timer.timeout.connect(self._webcam_tick)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Controls Header
        top_bar = FuturisticCard()
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        btn_load = NeonButton("Load Image", variant="cyan")
        btn_load.clicked.connect(self._load_image)
        top_layout.addWidget(btn_load)

        btn_default = NeonButton("Use FTech Logo", variant="purple")
        btn_default.clicked.connect(self._load_default_logo)
        top_layout.addWidget(btn_default)

        self.btn_webcam = NeonButton("🎥 Live Webcam", variant="green")
        self.btn_webcam.clicked.connect(self._toggle_webcam)
        top_layout.addWidget(self.btn_webcam)

        top_layout.addSpacing(15)

        top_layout.addWidget(QLabel("Operation:"))
        self.combo_ops = QComboBox()
        self.combo_ops.addItems([
            "🎯 Cyber Face & Eye HUD",
            "Canny Edge Detection",
            "Gaussian Blur",
            "Binary Threshold",
            "Adaptive Threshold",
            "Contour Extractor",
            "Heatmap (JET)",
            "Cyber Ocean Colormap"
        ])
        self.combo_ops.currentIndexChanged.connect(self._apply_operation)
        top_layout.addWidget(self.combo_ops)

        self.lbl_param = QLabel("Threshold: 100")
        top_layout.addWidget(self.lbl_param)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 255)
        self.slider.setValue(100)
        self.slider.setFixedWidth(120)
        self.slider.valueChanged.connect(self._on_slider_changed)
        top_layout.addWidget(self.slider)

        btn_save = NeonButton("Save Processed", variant="cyan")
        btn_save.clicked.connect(self._save_image)
        top_layout.addWidget(btn_save)

        top_layout.addStretch()

        self.stat_detected = StatCard("Targets / Contours", "0", color=THEME['accent_cyan'])
        self.stat_detected.setFixedHeight(50)
        top_layout.addWidget(self.stat_detected)

        top_bar.addLayout(top_layout)
        main_layout.addWidget(top_bar)

        # Side by Side Viewports
        viewport_layout = QHBoxLayout()
        viewport_layout.setSpacing(16)

        orig_card = FuturisticCard("ORIGINAL INPUT STREAM")
        self.lbl_orig = QLabel()
        self.lbl_orig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_orig.setMinimumSize(360, 340)
        self.lbl_orig.setStyleSheet(f"background-color: {THEME['bg_dark']}; border-radius: 8px;")
        orig_card.addWidget(self.lbl_orig)
        viewport_layout.addWidget(orig_card)

        proc_card = FuturisticCard("PROCESSED NEURAL / HUD VISION OUTPUT")
        self.lbl_proc = QLabel()
        self.lbl_proc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_proc.setMinimumSize(360, 340)
        self.lbl_proc.setStyleSheet(f"background-color: {THEME['bg_dark']}; border-radius: 8px;")
        proc_card.addWidget(self.lbl_proc)
        viewport_layout.addWidget(proc_card)

        main_layout.addLayout(viewport_layout)

        # Load default on start
        self._load_default_logo()

    def _load_default_logo(self):
        self._stop_webcam()
        if os.path.exists(LOGO_PATH):
            self.cv_engine.load_image(LOGO_PATH)
            self._update_views()
            self._apply_operation()

    def _load_image(self):
        self._stop_webcam()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            try:
                self.cv_engine.load_image(file_path)
                self._update_views()
                self._apply_operation()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _toggle_webcam(self):
        if self.webcam_timer.isActive():
            self._stop_webcam()
        else:
            try:
                self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    # Fallback default backend
                    self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    QMessageBox.warning(self, "Webcam Error", "No accessible camera found or permission denied.")
                    return
                self.btn_webcam.setText("⏹ Stop Webcam")
                self.webcam_timer.start()
            except Exception as e:
                QMessageBox.warning(self, "Webcam Error", f"Could not initialize webcam:\n{e}")

    def _stop_webcam(self):
        if self.webcam_timer.isActive():
            self.webcam_timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.btn_webcam.setText("🎥 Live Webcam")

    def _webcam_tick(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.cv_engine.set_image(frame)
                self._update_views()
                self._apply_operation()

    def _on_slider_changed(self, val: int):
        op = self.combo_ops.currentText()
        if "Blur" in op:
            self.lbl_param.setText(f"Kernel: {val}")
        else:
            self.lbl_param.setText(f"Threshold: {val}")
        self._apply_operation()

    def _apply_operation(self):
        op = self.combo_ops.currentText()
        val = self.slider.value()

        if "Face" in op:
            img, count = self.cv_engine.apply_cyber_face_detect()
            self.stat_detected.set_value(f"{count} Faces")
        elif op == "Canny Edge Detection":
            self.cv_engine.apply_canny(th1=val, th2=val*2)
            self.stat_detected.set_value("Edges Active")
        elif op == "Gaussian Blur":
            k = max(1, val if val % 2 == 1 else val + 1)
            self.cv_engine.apply_blur(kernel_size=k)
            self.stat_detected.set_value(f"K={k}")
        elif op == "Binary Threshold":
            self.cv_engine.apply_threshold(th=val, method="Binary")
            self.stat_detected.set_value(f"Th={val}")
        elif op == "Adaptive Threshold":
            self.cv_engine.apply_threshold(method="Adaptive")
            self.stat_detected.set_value("Gaussian")
        elif op == "Contour Extractor":
            img, count = self.cv_engine.apply_contours()
            self.stat_detected.set_value(f"{count} Contours")
        elif op == "Heatmap (JET)":
            self.cv_engine.apply_colormap("JET")
            self.stat_detected.set_value("JET Map")
        elif op == "Cyber Ocean Colormap":
            self.cv_engine.apply_colormap("CYBER_COOL")
            self.stat_detected.set_value("Ocean Map")

        self._update_processed_view()

    def _cv_to_pixmap(self, cv_img):
        if cv_img is None:
            return QPixmap()
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(q_img).scaled(
            420, 380,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    def _update_views(self):
        if self.cv_engine.original_image is not None:
            pix = self._cv_to_pixmap(self.cv_engine.original_image)
            self.lbl_orig.setPixmap(pix)

    def _update_processed_view(self):
        if self.cv_engine.processed_image is not None:
            pix = self._cv_to_pixmap(self.cv_engine.processed_image)
            self.lbl_proc.setPixmap(pix)

    def _save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "processed_vision.png", "Images (*.png *.jpg)")
        if file_path:
            try:
                self.cv_engine.save_processed(file_path)
                QMessageBox.information(self, "Saved", f"Image saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def hideEvent(self, event):
        # Stop webcam if tab changed to save CPU
        self._stop_webcam()
        super().hideEvent(event)
