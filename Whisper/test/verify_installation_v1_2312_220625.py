import sys
import os
import subprocess

def check_installation():
    try:
        # Check Python path
        print(f"Python executable: {sys.executable}")
        
        # Check if faster_whisper is in path
        import faster_whisper
        print("faster_whisper imported successfully")
        print(f"Location: {os.path.dirname(faster_whisper.__file__)}")
        return True
        
    except ImportError:
        print("faster_whisper not found in Python path")
        print("Current Python path:")
        for p in sys.path:
            print(f" - {p}")
        return False

if __name__ == "__main__":
    check_installation()
