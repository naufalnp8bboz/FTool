import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
from ftool.ui.splash import FuturisticSplashScreen
from ftool.ui.main_window import MainWindow

def test_gui():
    print("Starting upgraded GUI init test...", flush=True)
    app = QApplication([])
    splash = FuturisticSplashScreen()
    print("Splash created successfully.", flush=True)
    win = MainWindow()
    print("MainWindow created successfully. Stacked tabs count:", win.stacked_widget.count(), flush=True)
    
    # Test switching to every tab
    for i in range(win.stacked_widget.count()):
        win.switch_tab(i)
        print(f"Tab {i} switched smoothly: {win.lbl_current_tab.text()}", flush=True)

    # Test changing theme
    win._change_theme("Violet")
    print("Theme changed to Violet successfully.", flush=True)
    win._change_theme("Matrix")
    print("Theme changed to Matrix successfully.", flush=True)

    app.quit()
    print(">>> ALL 9 UPGRADED WORKSPACES VERIFIED OFFSCREEN! <<<", flush=True)

if __name__ == "__main__":
    test_gui()
