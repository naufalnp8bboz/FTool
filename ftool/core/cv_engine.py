import os
import cv2
import numpy as np
from typing import Optional, Tuple, List

class CVEngine:
    def __init__(self):
        self.original_image: Optional[np.ndarray] = None
        self.processed_image: Optional[np.ndarray] = None
        
        # Load Haar cascades
        face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path) if os.path.exists(face_cascade_path) else None
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path) if os.path.exists(eye_cascade_path) else None

    def load_image(self, filepath: str) -> np.ndarray:
        img = cv2.imread(filepath)
        if img is None:
            raise ValueError("Could not open image file.")
        self.original_image = img
        self.processed_image = img.copy()
        return self.original_image

    def set_image(self, img: np.ndarray):
        self.original_image = img.copy()
        self.processed_image = img.copy()

    def reset(self) -> np.ndarray:
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            return self.processed_image
        return np.zeros((100, 100, 3), dtype=np.uint8)

    def apply_cyber_face_detect(self) -> Tuple[np.ndarray, int]:
        """Detects faces and eyes, drawing cyberpunk neon targeting reticles."""
        if self.original_image is None or self.face_cascade is None:
            return np.zeros((100, 100, 3), dtype=np.uint8), 0

        output = self.original_image.copy()
        gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))

        for idx, (x, y, w, h) in enumerate(faces):
            # Cyber HUD Corner Brackets (Neon Cyan: (255, 229, 0) in BGR)
            corner_len = max(10, int(w * 0.2))
            thickness = 2
            cyan = (255, 229, 0)
            
            # Top-Left
            cv2.line(output, (x, y), (x + corner_len, y), cyan, thickness)
            cv2.line(output, (x, y), (x, y + corner_len), cyan, thickness)
            # Top-Right
            cv2.line(output, (x + w, y), (x + w - corner_len, y), cyan, thickness)
            cv2.line(output, (x + w, y), (x + w, y + corner_len), cyan, thickness)
            # Bottom-Left
            cv2.line(output, (x, y + h), (x + corner_len, y + h), cyan, thickness)
            cv2.line(output, (x, y + h), (x, y + h - corner_len), cyan, thickness)
            # Bottom-Right
            cv2.line(output, (x + w, y + h), (x + w - corner_len, y + h), cyan, thickness)
            cv2.line(output, (x + w, y + h), (x + w, y + h - corner_len), cyan, thickness)

            # Center crosshair
            cx, cy = x + w // 2, y + h // 2
            cv2.drawMarker(output, (cx, cy), cyan, markerType=cv2.MARKER_CROSS, markerSize=12, thickness=1)

            # Target label
            cv2.putText(output, f"[TARGET_LOCKED: #{idx+1}]", (x, max(15, y - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, cyan, 1, cv2.LINE_AA)

            # Eye detection inside face ROI
            if self.eye_cascade:
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = output[y:y+h, x:x+w]
                eyes = self.eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=8, minSize=(15, 15))
                for (ex, ey, ew, eh) in eyes:
                    ecx, ecy = ex + ew // 2, ey + eh // 2
                    # Violet ring (BGR: 255, 77, 124)
                    cv2.circle(roi_color, (ecx, ecy), max(6, ew // 2), (255, 77, 124), 1)

        self.processed_image = output
        return self.processed_image, len(faces)

    def apply_canny(self, th1: int = 100, th2: int = 200) -> np.ndarray:
        if self.original_image is None:
            return np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, th1, th2)
        self.processed_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return self.processed_image

    def apply_blur(self, kernel_size: int = 5) -> np.ndarray:
        if self.original_image is None:
            return np.zeros((100, 100, 3), dtype=np.uint8)
        k = max(1, kernel_size if kernel_size % 2 == 1 else kernel_size + 1)
        self.processed_image = cv2.GaussianBlur(self.original_image, (k, k), 0)
        return self.processed_image

    def apply_threshold(self, th: int = 127, method: str = "Binary") -> np.ndarray:
        if self.original_image is None:
            return np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        if method == "Otsu":
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == "Adaptive":
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        else:
            _, thresh = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY)
        self.processed_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        return self.processed_image

    def apply_colormap(self, colormap_name: str = "JET") -> np.ndarray:
        if self.original_image is None:
            return np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        mapping = {
            "JET": cv2.COLORMAP_JET,
            "HOT": cv2.COLORMAP_HOT,
            "VIRIDIS": cv2.COLORMAP_VIRIDIS,
            "BONE": cv2.COLORMAP_BONE,
            "CYBER_COOL": cv2.COLORMAP_OCEAN
        }
        cm = mapping.get(colormap_name, cv2.COLORMAP_JET)
        self.processed_image = cv2.applyColorMap(gray, cm)
        return self.processed_image

    def apply_contours(self) -> Tuple[np.ndarray, int]:
        if self.original_image is None:
            return np.zeros((100, 100, 3), dtype=np.uint8), 0
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        output = self.original_image.copy()
        cv2.drawContours(output, contours, -1, (0, 255, 128), 2)
        self.processed_image = output
        return self.processed_image, len(contours)

    def save_processed(self, filepath: str):
        if self.processed_image is not None:
            cv2.imwrite(filepath, self.processed_image)
