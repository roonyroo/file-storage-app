import sys
import subprocess

print(f"Python Path: {sys.executable}")
print(f"Python Version: {sys.version}")

# Check installed packages
print("\nInstalled Packages:")
subprocess.run([sys.executable, "-m", "pip", "list"])
