import sys
import subprocess

def check_pyaudio():
    try:
        import pyaudio
        print("PyAudio is installed and importable")
        return True
    except ImportError:
        print("PyAudio not found")
        return False

if __name__ == "__main__":
    print(f"Using Python: {sys.executable}")
    if not check_pyaudio():
        print("Attempting to install PyAudio...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyaudio"])
