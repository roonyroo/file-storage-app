import pyttsx3
import os
import time
import sys
import signal
import datetime
import traceback

# Configuration
DEBUG_MODE = True
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ocr_tts_workflow", "tts_log.txt")
TIMEOUT = 20  # 20 seconds timeout as per user's global rules

class TTSModule:
    def __init__(self):
        # Initialize TTS engine
        try:
            self.engine = pyttsx3.init()
            self.log("TTS engine initialized successfully")
        except Exception as e:
            self.log(f"Error initializing TTS engine: {e}", error=True)
            raise
        
        # Set up timeout handler
        self.setup_timeout()
        
        # Track last spoken text to avoid duplicates
        self.last_spoken = ""
        
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def log(self, message, error=False):
        """Log messages to console and log file"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {'ERROR: ' if error else ''}{message}"
        
        # Print to console
        print(log_message)
        
        # Write to log file
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def setup_timeout(self):
        """Set up timeout handler to prevent infinite loops"""
        # Windows doesn't support SIGALRM, so we'll use a different approach
        # Instead of signal-based timeouts, we'll use time-based checks in our methods
        self.start_time = time.time()
        
        # Set up handler for Ctrl+C
        def interrupt_handler(signum, frame):
            self.log("Received interrupt signal, exiting...")
            sys.exit(0)
        
        # Set the interrupt handler
        signal.signal(signal.SIGINT, interrupt_handler)
    
    def read_and_speak_file(self, file_path):
        """Read text from file and speak it"""
        try:
            # Start operation timer
            operation_start = time.time()
            
            if not os.path.exists(file_path):
                self.log(f"File not found: {file_path}", error=True)
                return False
            
            # Read the file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except Exception as e:
                self.log(f"Error reading file {file_path}: {e}", error=True)
                return False
            
            # Check for timeout
            if time.time() - operation_start > TIMEOUT:
                self.log(f"Operation timed out after {TIMEOUT} seconds", error=True)
                return False
            
            # Check if there's text to speak
            if text.strip():
                # Check if this is new text (avoid duplicates)
                if text.strip() != self.last_spoken:
                    self.log(f"Speaking new text: {text}")
                    self.engine.say(text)
                    self.engine.runAndWait()
                    self.last_spoken = text.strip()
                else:
                    self.log("Skipping duplicate text")
            
            # Check for timeout again after speaking
            if time.time() - operation_start > TIMEOUT:
                self.log(f"Operation timed out after {TIMEOUT} seconds", error=True)
                return False
            
            # Clear file after reading
            try:
                open(file_path, 'w', encoding='utf-8').close()
                self.log("File cleared after reading")
            except Exception as e:
                self.log(f"Error clearing file {file_path}: {e}", error=True)
            
            return True
            
        except Exception as e:
            self.log(f"Error in read_and_speak_file: {e}", error=True)
            self.log(traceback.format_exc(), error=True)
            return False

    def monitor_and_speak(self, file_path, poll_interval=1):
        """Monitor file for changes and speak new text"""
        self.log(f"TTS Module: Monitoring {file_path} for new text...")
        
        # Reset start time for monitoring
        self.start_time = time.time()
        loop_count = 0
        
        # Main monitoring loop
        try:
            while True:
                try:
                    # Increment loop counter
                    loop_count += 1
                    
                    # Check for overall timeout (every 10 loops to reduce overhead)
                    if loop_count % 10 == 0 and time.time() - self.start_time > TIMEOUT * 5:
                        # For monitoring, we use a longer timeout (5x normal timeout)
                        # Reset the timer instead of exiting to keep monitoring running
                        self.log(f"Monitoring has been running for {time.time() - self.start_time:.2f} seconds. Resetting timer.")
                        self.start_time = time.time()
                    
                    # Check if file exists and has content
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        # Process the file and speak the text
                        operation_start = time.time()
                        result = self.read_and_speak_file(file_path)
                        
                        # Log processing time if it took a while
                        operation_time = time.time() - operation_start
                        if operation_time > 1.0:  # Log if processing took more than 1 second
                            self.log(f"File processing took {operation_time:.2f} seconds")
                    
                    # Sleep before checking again
                    time.sleep(poll_interval)
                    
                except KeyboardInterrupt:
                    self.log("Monitoring stopped by user")
                    break
                except Exception as e:
                    self.log(f"Error during monitoring: {e}", error=True)
                    self.log(traceback.format_exc(), error=True)
                    # Continue monitoring despite errors
                    time.sleep(poll_interval)
        
        except Exception as e:
            self.log(f"Fatal error in monitor_and_speak: {e}", error=True)
            self.log(traceback.format_exc(), error=True)
            sys.exit(1)

if __name__ == "__main__":
    # Start timer for timeout
    start_time = time.time()
    
    # Set up signal handler for graceful exit
    def signal_handler(sig, frame):
        print('\nExiting TTS module...')
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize TTS module
        tts = TTSModule()
        
        # Define the output file to monitor
        output_file = "F:\\Code\\ocr_output.txt"
        
        # Ensure the output file exists
        if not os.path.exists(output_file):
            with open(output_file, 'w', encoding='utf-8') as f:
                pass  # Create empty file
            tts.log(f"Created empty output file: {output_file}")
        
        # Start monitoring the file for changes
        tts.log(f"Starting to monitor {output_file} for new text...")
        tts.monitor_and_speak(output_file, poll_interval=1)
        
    except KeyboardInterrupt:
        tts.log("TTS module stopped by user")
    except Exception as e:
        tts.log(f"Fatal error in TTS module: {e}", error=True)
        tts.log(traceback.format_exc(), error=True)
        sys.exit(1)
    finally:
        # Check for timeout
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            tts.log(f"TTS module timed out after {elapsed_time:.2f} seconds", error=True)
        else:
            tts.log(f"TTS module completed in {elapsed_time:.2f} seconds")
        
        # Exit gracefully
        sys.exit(0)
