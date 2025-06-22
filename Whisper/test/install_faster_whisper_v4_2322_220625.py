import sys
import subprocess

PYTHON_PATH = r"C:\Program Files\Python313\python.exe"
SITE_PACKAGES = r"C:\Program Files\Python313\Lib\site-packages"

try:
    subprocess.run(
        [PYTHON_PATH, "-m", "pip", "install", "faster-whisper",
         "--target", SITE_PACKAGES],
        check=True
    )
    print("faster-whisper installed to system site-packages")
except Exception as e:
    print(f"Installation failed: {e}")
    sys.exit(1)
