import os
import sys
import subprocess
import shutil

def build():
    print("==================================================")
    print("   FTool Windows Executable Builder (FTech)       ")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    assets_dir = os.path.join(base_dir, "assets")
    icon_path = os.path.join(assets_dir, "app_icon.ico")
    main_py = os.path.join(base_dir, "main.py")

    # PyInstaller arguments
    # Using ; for Windows separator in --add-data
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=FTool",
        "--noconfirm",
        "--clean",
        "--windowed", # No terminal console pop-up
        f"--icon={icon_path}",
        f"--add-data=assets;assets",
        "--hidden-import=sklearn.utils._typedefs",
        "--hidden-import=sklearn.neighbors._typedefs",
        "--hidden-import=matplotlib.backends.backend_qtagg",
        "--collect-all=sklearn",
        main_py
    ]

    print("Running PyInstaller command:")
    print(" ".join(cmd))
    print("\nCompiling... (this may take 1-2 minutes)")
    
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\n==================================================")
        print("[SUCCESS] FTool.exe built successfully!")
        dist_path = os.path.join(base_dir, "dist", "FTool", "FTool.exe")
        print(f"Executable location: {dist_path}")
        print("==================================================")
    else:
        print("\n[ERROR] Build failed with return code:", result.returncode)

if __name__ == "__main__":
    build()
