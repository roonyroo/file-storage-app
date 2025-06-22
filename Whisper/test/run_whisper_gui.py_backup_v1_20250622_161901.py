import os
import sys
import time
import subprocess
import logging
from datetime import datetime
import traceback

# Explicit Python interpreter path (matches working verification script)
PYTHON_PATH = r"C:\Program Files\Python313\python.exe"
if not os.path.exists(PYTHON_PATH):
    print(f"Python interpreter not found at {PYTHON_PATH}")
    sys.exit(1)

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
try:
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
except Exception as e:
    print(f"Failed to initialize logging: {e}")
    sys.exit(1)

def run_with_restart():
    """Run the whisper GUI application and restart it if it crashes."""
    max_restarts = 5
    restart_count = 0
    restart_delay = 2  # seconds
    
    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'whisper_gui.py')
    
    print("="*50)
    print("Whisper GUI Auto-Restart Launcher")
    print("="*50)
    print(f"Log file: {log_file}")
    print("This launcher will automatically restart the application if it crashes.")
    print("Press Ctrl+C in this terminal to completely exit.")
    print("="*50)
    
    try:
        while restart_count < max_restarts:
            try:
                if restart_count > 0:
                    print(f"\nRestarting application (attempt {restart_count}/{max_restarts})...")
                    logger.info(f"Restarting application (attempt {restart_count}/{max_restarts})")
                    time.sleep(restart_delay)
                
                logger.info(f"Starting Whisper GUI application")
                print(f"\nStarting Whisper GUI application...")
                
                # Run the GUI application as a subprocess
                process = subprocess.run([python_executable, script_path], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE,
                                        text=True)
                
                # If the process exited with a non-zero status, it crashed
                if process.returncode != 0:
                    logger.error(f"Application exited with code {process.returncode}")
                    logger.error(f"STDOUT: {process.stdout}")
                    logger.error(f"STDERR: {process.stderr}")
                    
                    print(f"\nApplication crashed with exit code {process.returncode}")
                    restart_count += 1
                else:
                    # Normal exit
                    logger.info("Application exited normally")
                    print("\nApplication closed normally.")
                    break
                    
            except KeyboardInterrupt:
                logger.info("User interrupted the launcher")
                print("\nLauncher interrupted by user. Exiting...")
                break
        if restart_count >= max_restarts:
            logger.error("Maximum restart attempts reached. Giving up.")
            print("\nMaximum restart attempts reached. Please check the logs for errors.")
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        logging.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    run_with_restart()
