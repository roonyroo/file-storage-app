import os
import sys
import subprocess

# Verify Python path
python_path = r"C:\Program Files\Python313\python.exe"
print(f"Using Python: {python_path}")
print(f"Exists: {os.path.exists(python_path)}")

# Check installed packages
print("\nChecking packages:")
subprocess.run([python_path, "-m", "pip", "list"], stdout=sys.stdout, stderr=sys.stderr)

# Run whisper_gui.py with full output
print("\nRunning whisper_gui.py:")
subprocess.run([python_path, "e:\\whisper_test\\run_whisper_gui.py"], stdout=sys.stdout, stderr=sys.stderr)
