import sys
import subprocess

PYTHON_PATH = r"C:\Program Files\Python313\python.exe"

# First install required dependencies
try:
    subprocess.run([PYTHON_PATH, "-m", "pip", "install", "torch", "torchaudio"], check=True)
    print("Dependencies installed successfully")
    
    # Then install faster-whisper
    subprocess.run([PYTHON_PATH, "-m", "pip", "install", "faster-whisper"], check=True)
    print("faster-whisper installed successfully")
    
except Exception as e:
    print(f"Installation failed: {e}")
    sys.exit(1)
