import cv2
import numpy as np
from typing import Optional, Tuple

class CVEngine:
    def __init__(self):
        self.original_image: Optional[np.ndarray] = None
        self.processed_image: Optional[np.ndarray] = None

    def load_image(self, filepath: str) -> np.ndarray:
        img = cv2.imread(filepath)
        if img is None:
            raise ValueError("Could not open image file.")
        self.original_image = img
        self.processed_image = img.copy()
        return self.original_image

    def set_image(self, img: np.ndarray):
        self.original_image = img
        self.processed_image = img.copy()

    def reset(self) -> np.ndarray:
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            return self.processed_image
        return np.zeros((100, 100, 3), dtype=np.uint8)

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
        k = max(1, kernel_size)
        if k % 2 == 0:
            k += 1
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
        # Draw glowing neon green contours
        cv2.drawContours(output, contours, -1, (0, 255, 128), 2)
        self.processed_image = output
        return self.processed_image, len(contours)

    def save_processed(self, filepath: str):
        if self.processed_image is not None:
            cv2.imwrite(filepath, self.processed_image)
