import sys
import subprocess

try:
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Architecture: {'64-bit' if sys.maxsize > 2**32 else '32-bit'}")
    
    # Check if pyaudio is installed in this environment
    try:
        import pyaudio
        print("Pyaudio is available")
    except ImportError:
        print("Pyaudio is NOT available")
    
    # List all installed packages
    print("\nInstalled packages:")
    subprocess.call([sys.executable, "-m", "pip", "list"])
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
