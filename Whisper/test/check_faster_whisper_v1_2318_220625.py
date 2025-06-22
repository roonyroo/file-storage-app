import sys
import subprocess

PYTHON_PATH = r"C:\Program Files\Python313\python.exe"

try:
    result = subprocess.run(
        [PYTHON_PATH, "-m", "pip", "show", "faster-whisper"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if not result.stdout:
        print("faster-whisper not installed in target environment")
except Exception as e:
    print(f"Error checking installation: {e}")
