import sys
import subprocess

PYTHON_PATH = r"C:\Program Files\Python313\python.exe"

try:
    subprocess.run([PYTHON_PATH, "-m", "pip", "install", "faster-whisper"], check=True)
    print("faster-whisper installed successfully")
except Exception as e:
    print(f"Installation failed: {e}")
    sys.exit(1)
