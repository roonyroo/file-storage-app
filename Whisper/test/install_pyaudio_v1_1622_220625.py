import sys
import subprocess

try:
    print("Installing pyaudio...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"], stdout=sys.stdout, stderr=sys.stderr)
    print("Successfully installed pyaudio")
except subprocess.CalledProcessError as e:
    print(f"Error installing pyaudio: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
