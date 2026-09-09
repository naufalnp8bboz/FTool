import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ftool.config import ICON_PATH
from ftool.ui.splash import FuturisticSplashScreen
from ftool.ui.main_window import MainWindow

def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("FTool")
    app.setOrganizationName("FTech")

    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    # Create splash screen with 3-second animated fade
    splash = FuturisticSplashScreen()
    main_win = None

    def on_splash_finish():
        nonlocal main_win
        main_win = MainWindow()
        main_win.show()

    splash.finished.connect(on_splash_finish)
    splash.start_splash()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
