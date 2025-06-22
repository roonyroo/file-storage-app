import sys
import subprocess

try:
    print("Installing faster-whisper...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "faster-whisper"], stdout=sys.stdout, stderr=sys.stderr)
    print("Successfully installed faster-whisper")
except subprocess.CalledProcessError as e:
    print(f"Error installing faster-whisper: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
