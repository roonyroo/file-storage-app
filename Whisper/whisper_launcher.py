#!/usr/bin/env python
"""
Whisper GUI Launcher
--------------------
Consolidated wrapper script that handles Python environment,
dependencies, and launches the Whisper GUI application.
"""
import os
import sys
import time
import subprocess
import logging
from datetime import datetime

# Configuration
PYTHON_PATH = r"C:\Program Files\Python313\python.exe"
APP_PATH = os.path.dirname(os.path.abspath(__file__))
WHISPER_GUI_PATH = os.path.join(APP_PATH, "whisper_gui.py")
DEPENDENCIES = ["pyaudio", "faster-whisper"]

# Set up logging
log_dir = os.path.join(APP_PATH, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"whisper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('whisper_launcher')
logger.info(f"Logging initialized. Log file: {log_file}")

def check_dependencies():
    """Check and install required dependencies if needed."""
    try:
        # Check Python version
        if not os.path.exists(PYTHON_PATH):
            logger.error(f"Python interpreter not found at {PYTHON_PATH}")
            print(f"Error: Python interpreter not found at {PYTHON_PATH}")
            sys.exit(1)
            
        # Verify dependencies
        for dep in DEPENDENCIES:
            result = subprocess.run(
                [PYTHON_PATH, "-m", "pip", "show", dep],
                capture_output=True,
                text=True
            )
            if not result.stdout:
                logger.warning(f"{dep} not installed, attempting to install...")
                subprocess.run([PYTHON_PATH, "-m", "pip", "install", dep], check=True)
                logger.info(f"{dep} installed successfully")
            else:
                logger.info(f"{dep} is already installed")
        return True
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
        print(f"Error checking dependencies: {e}")
        return False

def run_with_restart():
    """Run the Whisper GUI application with auto-restart capability."""
    logger.info("Starting Whisper GUI application")
    print("Starting Whisper GUI application...")
    print("=" * 50)
    print("Whisper GUI Auto-Restart Launcher")
    print("=" * 50)
    print(f"Log file: {log_file}")
    print("This launcher will automatically restart the application if it crashes.")
    print("Press Ctrl+C in this terminal to completely exit.")
    print("=" * 50)
    
    while True:
        try:
            # Run the application
            process = subprocess.run(
                [PYTHON_PATH, WHISPER_GUI_PATH],
                cwd=APP_PATH
            )
            
            # Check exit code
            if process.returncode == 0:
                logger.info("Application exited normally")
                print("\nApplication closed normally.")
                break
            else:
                logger.warning(f"Application crashed with exit code {process.returncode}, restarting...")
                print(f"\nApplication crashed with exit code {process.returncode}, restarting in 3 seconds...")
                time.sleep(3)
                
        except KeyboardInterrupt:
            logger.info("User interrupted application")
            print("\nExiting application by user request.")
            break
            
        except Exception as e:
            logger.error(f"Error running Whisper GUI: {e}")
            print(f"\nError: {e}")
            print("Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    if check_dependencies():
        run_with_restart()
    else:
        print("Failed to verify dependencies. Please check the log file.")
        sys.exit(1)
