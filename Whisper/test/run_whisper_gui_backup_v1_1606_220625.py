import os
import sys
import time
import subprocess
import logging
from datetime import datetime

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'whisper_launcher_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('whisper_launcher')

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
        except Exception as e:
            logger.error(f"Error in launcher: {str(e)}")
            print(f"\nError in launcher: {str(e)}")
            restart_count += 1
    
    if restart_count >= max_restarts:
        logger.error("Maximum restart attempts reached. Giving up.")
        print("\nMaximum restart attempts reached. Please check the logs for errors.")

if __name__ == "__main__":
    run_with_restart()
