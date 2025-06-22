import os
import tempfile
import wave
import pyaudio
import time
import numpy as np
import threading
import keyboard
import pyperclip
import tkinter as tk
import logging
import traceback
import sys
import subprocess
from datetime import datetime
from tkinter import ttk, messagebox, scrolledtext
from faster_whisper import WhisperModel

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'whisper_gui_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('whisper_gui')

class WhisperGUI:
    TRANSCRIPTION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcriptions.txt")
    
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Speech-to-Text")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set up error handling for the GUI
        self.root.report_callback_exception = self.handle_callback_error
        
        # Set style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", font=("Arial", 10))
        self.style.configure("TLabel", font=("Arial", 11))
        
        # Variables
        self.selected_language = tk.StringVar(value="English")
        self.selected_model = tk.StringVar(value="small")
        self.recording = False
        self.model = None
        self.transcription = ""
        self.recording_thread = None
        self.stop_recording = threading.Event()
        
        # Ensure transcription file exists
        open(self.TRANSCRIPTION_FILE, 'a').close()
        
        # Initialize PyAudio
        try:
            self.p = pyaudio.PyAudio()
            logger.info("PyAudio initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio: {str(e)}")
            messagebox.showerror("Error", f"Failed to initialize audio system: {str(e)}")
            raise
        
        # Initialize recording variables
        self.frames = []
        self.recording = False
        self.stop_recording = threading.Event()
        self.transcription = ""
        
        # Create frames
        self.create_settings_frame()
        self.create_recording_frame()
        self.create_transcription_frame()
        self.create_status_bar()
        
        # Load model
        self.load_model_thread = threading.Thread(target=self.load_model)
        self.load_model_thread.daemon = True
        self.load_model_thread.start()
        
        # Set up keyboard hooks
        try:
            keyboard.on_press_key("`", self.on_key_press)
            keyboard.on_press_key("caps lock", self.on_caps_lock)
            logger.info("Keyboard hooks set up successfully")
        except Exception as e:
            logger.error(f"Failed to set up keyboard hooks: {str(e)}")
            messagebox.showerror("Error", f"Failed to set up keyboard shortcuts: {str(e)}")
        
        # Set up closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_settings_frame(self):
        settings_frame = ttk.LabelFrame(self.root, text="Settings")
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        # Language selection
        ttk.Label(settings_frame, text="Language:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        languages = ["English", "Urdu", "Hindi", "Bengali", "Punjabi"]
        language_combo = ttk.Combobox(settings_frame, textvariable=self.selected_language, values=languages, state="readonly", width=15)
        language_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        language_combo.bind("<<ComboboxSelected>>", lambda e: self.load_model())
        
        # Model selection
        ttk.Label(settings_frame, text="Model:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        models = ["tiny", "base", "small", "medium"]
        model_combo = ttk.Combobox(settings_frame, textvariable=self.selected_model, values=models, state="readonly", width=10)
        model_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        model_combo.bind("<<ComboboxSelected>>", lambda e: self.load_model())
        
        # Help text
        help_text = "Press ` (backtick) to start recording, CAPS LOCK to stop"
        ttk.Label(settings_frame, text=help_text).grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="w")
    
    def create_recording_frame(self):
        recording_frame = ttk.Frame(self.root)
        recording_frame.pack(fill="x", padx=10, pady=5)
        
        self.record_button = ttk.Button(recording_frame, text="Start Recording (or press `)", command=self.toggle_recording)
        self.record_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(recording_frame, text="Stop Recording (or press CAPS LOCK)", command=self.stop_recording_action, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # Add keyboard shortcut for pasting
        self.root.bind('<Alt-v>', lambda e: self.paste_text())
        
        # Audio level meter
        self.level_frame = ttk.Frame(self.root)
        self.level_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(self.level_frame, text="Audio Level:").pack(side="left", padx=5)
        
        self.level_canvas = tk.Canvas(self.level_frame, height=20, width=400, bg="white")
        self.level_canvas.pack(side="left", padx=5, fill="x", expand=True)
    
    def create_transcription_frame(self):
        transcription_frame = ttk.LabelFrame(self.root, text="Transcription")
        transcription_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.transcription_text = tk.Text(transcription_frame, wrap="word", height=10)
        self.transcription_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(transcription_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        self.copy_button = ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(side="left", padx=5)
        
        self.paste_button = ttk.Button(button_frame, text="Paste (after 2s)", command=self.paste_text)
        self.paste_button.pack(side="left", padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_transcription)
        self.clear_button.pack(side="left", padx=5)
    
    def create_status_bar(self):
        # Status bar at the bottom
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")
        
        # Add log viewer button
        log_button = ttk.Button(self.root, text="View Logs", command=self.show_logs)
        log_button.pack(side="bottom", pady=5)
    
    def show_logs(self):
        """Show logs in a new window"""
        log_window = tk.Toplevel(self.root)
        log_window.title("Application Logs")
        log_window.geometry("700x500")
        
        # Create a scrolled text widget to display logs
        log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD)
        log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Read and display the log file
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
                log_text.insert(tk.END, log_content)
                log_text.see(tk.END)  # Scroll to the end
        except Exception as e:
            log_text.insert(tk.END, f"Error reading log file: {str(e)}")
    
    def load_model(self):
        self.status_var.set("Loading model... Please wait")
        self.root.update_idletasks()
        
        # Create a progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Whisper Model Download")
        progress_window.geometry("500x200")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Progress display
        ttk.Label(progress_window, text="Downloading Whisper model...").pack(pady=10)
        progress_text = scrolledtext.ScrolledText(progress_window, height=8)
        progress_text.pack(fill="both", expand=True, padx=10, pady=10)
        progress_text.insert(tk.END, "Starting model download...\n")
        
        # Progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(fill="x", padx=10, pady=10)
        
        # Custom progress callback for huggingface_hub
        def progress_callback(progress):
            if progress.total:
                percent = (progress.completed * 100) / progress.total
                self.root.after(0, lambda: progress_var.set(percent))
                status = f"Downloading: {progress.completed/1024/1024:.1f}MB / {progress.total/1024/1024:.1f}MB ({percent:.1f}%)"
                self.root.after(0, lambda: progress_text.insert(tk.END, f"{status}\n"))
                self.root.after(0, lambda: progress_text.see(tk.END))
                self.root.after(0, lambda: self.status_var.set(status))
                self.root.update_idletasks()
        
        try:
            # Get language code
            language_codes = {
                "English": "en",
                "Urdu": "ur",
                "Hindi": "hi",
                "Bengali": "bn",
                "Punjabi": "pa"
            }
            language = language_codes.get(self.selected_language.get(), "en")
            model_size = self.selected_model.get()
            
            logger.info(f"Loading model: {model_size} for language: {self.selected_language.get()}")
            progress_text.insert(tk.END, f"Selected model: {model_size}\n")
            
            # Set huggingface_hub to show progress
            from huggingface_hub import HfFolder, snapshot_download
            import functools
            import os
            
            # Force redownload if needed for testing
            # os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
            # os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
            
            # Load the model with progress display
            try:
                # First try to download the model files to show progress
                progress_text.insert(tk.END, "Checking for model in cache...\n")
                model_id = f"guillaumekln/faster-whisper-{model_size}"
                
                # Try loading the model directly first - if it's already downloaded this will be fast
                self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
                progress_text.insert(tk.END, "Model already downloaded and loaded successfully!\n")
                
            except Exception as e:
                # If direct loading fails, try explicit download with progress callback
                progress_text.insert(tk.END, f"Downloading model: {model_id}\nThis may take several minutes for larger models.\n")
                progress_text.see(tk.END)
                
                # Import with custom callback for progress
                os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '1'
                
                # Try downloading with progress bar
                from huggingface_hub import hf_hub_download
                
                # Use a callback wrapper to update the UI
                self.model = WhisperModel(model_size, device="cpu", compute_type="int8", download_root=None)
            
            self.status_var.set(f"Model loaded: {model_size} - Language: {self.selected_language.get()}")
            logger.info(f"Model loaded successfully")
            progress_text.insert(tk.END, "Model loaded successfully!\n")
            
            # Close button enabled when finished
            close_button = ttk.Button(progress_window, text="Close", command=progress_window.destroy)
            close_button.pack(pady=10)
            
        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.status_var.set(error_msg)
            progress_text.insert(tk.END, f"ERROR: {error_msg}\n{traceback.format_exc()}\n")
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            
            # Close button for error case
            close_button = ttk.Button(progress_window, text="Close", command=progress_window.destroy)
            close_button.pack(pady=10)
    
    def on_key_press(self, event):
        # Start recording on backtick
        if event.name == '`' and event.event_type == keyboard.KEY_DOWN and not self.recording:
            self.toggle_recording()
            return False  # Block the key
        
        # Stop recording on Caps Lock
        if event.name == 'caps lock' and event.event_type == keyboard.KEY_DOWN and self.recording:
            self.stop_recording_action()
            return False  # Block the key
    
    def on_caps_lock(self, event):
        if event.event_type == keyboard.KEY_DOWN and self.recording:
            self.stop_recording_action()
            return False  # Block the key
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording_action()
    
    def start_recording(self):
        if self.recording:
            return
        
        self.recording = True
        self.frames = []
        self.stop_recording.clear()
        
        # Update UI
        self.record_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_var.set("Recording... (Press CAPS LOCK to stop)")
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def stop_recording_action(self):
        if not self.recording:
            return
        
        self.stop_recording.set()
        self.status_var.set("Processing audio...")
        logger.info("Recording stopped by user, processing audio")
        
        # Update UI
        self.record_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        
        # Wait a moment for the recording thread to finish
        self.root.after(500, self.check_recording_finished)
    
    def record_audio(self):
        logger.info("Starting audio recording")
        stream = None
        
        try:
            # Open audio stream
            stream = self.p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=16000,
                                input=True,
                                frames_per_buffer=1024)
            
            logger.debug("Audio stream opened successfully")
            
            # For audio level visualization
            last_update_time = time.time()
            
            while not self.stop_recording.is_set():
                # Read audio data
                data = stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
                
                # Update audio level meter every 100ms
                current_time = time.time()
                if current_time - last_update_time > 0.1:
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    volume = np.abs(audio_data).mean()
                    self.update_level_meter(volume)
                    last_update_time = current_time
            
            logger.info(f"Recording stopped, captured {len(self.frames)} frames")
            
            # Close the stream safely
            if stream and stream.is_active():
                stream.stop_stream()
                stream.close()
                stream = None
            
            # Process the recorded audio
            self.transcribe_audio()
            
        except Exception as e:
            error_msg = f"Error during recording: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.status_var.set(error_msg)
            messagebox.showerror("Error", f"Recording error: {str(e)}")
        
        finally:
            # Ensure stream is closed safely
            try:
                if stream is not None:
                    if hasattr(stream, 'is_active') and callable(stream.is_active):
                        if stream.is_active():
                            stream.stop_stream()
                    if hasattr(stream, 'close') and callable(stream.close):
                        stream.close()
                    logger.debug("Audio stream closed in finally block")
            except Exception as e:
                logger.error(f"Error closing stream: {str(e)}")
            
            self.recording = False
            self.root.after(0, lambda: self.record_button.configure(state="normal"))
            self.root.after(0, lambda: self.stop_button.configure(state="disabled"))
    
    def update_level_meter(self, volume):
        # Update the level meter on the main thread
        def _update():
            self.level_canvas.delete("all")
            max_volume = 5000  # Adjust based on your microphone sensitivity
            width = self.level_canvas.winfo_width()
            height = self.level_canvas.winfo_height()
            
            # Calculate bar width based on volume
            bar_width = min(int(volume / max_volume * width), width)
            
            # Draw the level bar
            self.level_canvas.create_rectangle(0, 0, bar_width, height, fill="green", outline="")
            
            # Add a red section for high levels
            if bar_width > width * 0.8:
                self.level_canvas.create_rectangle(width * 0.8, 0, bar_width, height, fill="red", outline="")
        
        self.root.after(0, _update)
    
    def check_recording_finished(self):
        """Check if recording thread has finished processing"""
        if hasattr(self, 'recording_thread') and self.recording_thread and self.recording_thread.is_alive():
            # Still processing, check again in 500ms
            self.root.after(500, self.check_recording_finished)
        else:
            # Recording thread is done, offer to paste
            if self.transcription:
                self.status_var.set("Ready to paste. Click 'Paste' or press Alt+V to paste in 2 seconds")
                # Enable paste button with focus
                self.paste_button.configure(state="normal")
                self.paste_button.focus_set()
    
    def transcribe_audio(self):
        if not self.frames:
            self.status_var.set("No audio recorded")
            logger.warning("Attempted to transcribe but no audio was recorded")
            return
        
        audio_path = None
        try:
            self.status_var.set("Saving audio...")
            logger.info(f"Saving audio recording ({len(self.frames)} frames)")
            
            # Save audio to a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                audio_path = temp_file.name
            
            with wave.open(audio_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(16000)
                wf.writeframes(b''.join(self.frames))
            
            logger.debug(f"Audio saved to temporary file: {audio_path}")
            self.status_var.set("Transcribing audio...")
            
            # Get language code
            language_codes = {
                "English": "en",
                "Urdu": "ur",
                "Hindi": "hi",
                "Bengali": "bn",
                "Punjabi": "pa"
            }
            language = language_codes.get(self.selected_language.get(), "en")
            logger.info(f"Transcribing audio in language: {language}")
            
            # Transcribe the audio
            segments, info = self.model.transcribe(audio_path, language=language)
            
            # Collect the transcription
            transcription = ""
            for segment in segments:
                transcription += segment.text + " "
            
            # Update the transcription text
            self.transcription = transcription.strip()
            logger.info(f"Transcription successful: {len(self.transcription)} characters")
            self.update_transcription_text()
            
            # Save transcription to file
            self.save_transcription(transcription)
            
            # Copy to clipboard
            try:
                pyperclip.copy(self.transcription)
                logger.info("Transcription copied to clipboard")
                
                # Automatically paste the text after a delay (like in mic_test.py)
                self.status_var.set("Auto-pasting text in 2 seconds... Switch to target window")
                logger.info("Auto-pasting text in 2 seconds")
                self.root.after(2000, self.auto_paste)
            except Exception as e:
                logger.error(f"Failed to copy to clipboard: {str(e)}")
                logger.error(traceback.format_exc())
            
            # Clean up
            if os.path.exists(audio_path):
                os.remove(audio_path)
                logger.debug("Temporary audio file removed")
            
            self.status_var.set("Transcription complete and copied to clipboard")
            
        except Exception as e:
            error_msg = f"Transcription error: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.status_var.set(error_msg)
            messagebox.showerror("Error", f"Transcription error: {str(e)}")
            
        finally:
            # Make sure temporary file is removed
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    logger.debug("Temporary audio file removed in finally block")
                except:
                    pass
    
    def save_transcription(self, text):
        """Save transcription to file for TTS module"""
        try:
            with open(self.TRANSCRIPTION_FILE, 'a', encoding='utf-8') as f:
                f.write(text + '\n')
            logger.info(f"Saved transcription to {self.TRANSCRIPTION_FILE}")
        except Exception as e:
            logger.error(f"Error saving transcription: {e}")
    
    def update_transcription_text(self):
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.insert(tk.END, self.transcription)
    
    def copy_to_clipboard(self):
        if self.transcription:
            pyperclip.copy(self.transcription)
            self.status_var.set("Transcription copied to clipboard")
    
    def paste_text(self):
        if self.transcription:
            self.status_var.set("Will paste text in 2 seconds... Switch to target window")
            logger.info("Preparing to paste text in 2 seconds")
            # Temporarily disable the button to prevent multiple clicks
            self.paste_button.configure(state="disabled")
            
            # Show countdown
            self.show_countdown(2)
            
    def show_countdown(self, seconds):
        """Show a countdown before pasting"""
        if seconds > 0:
            self.status_var.set(f"Pasting in {seconds} seconds... Switch to target window")
            self.root.after(1000, lambda: self.show_countdown(seconds - 1))
        else:
            self.perform_paste()
    
    def perform_paste(self):
        try:
            # Re-copy to clipboard to ensure it's still there
            pyperclip.copy(self.transcription)
            logger.info("Re-copied text to clipboard before pasting")
            
            # Use ctrl+v to paste - this matches the original mic_test.py implementation
            keyboard.press_and_release('ctrl+v')
            
            self.status_var.set("Text pasted")
            logger.info("Text pasted successfully")
            
            # Re-enable paste button
            self.paste_button.configure(state="normal")
        except Exception as e:
            error_msg = f"Error pasting: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.status_var.set(error_msg)
            messagebox.showerror("Error", f"Failed to paste: {str(e)}")
            # Re-enable paste button
            self.paste_button.configure(state="normal")
            
    def auto_paste(self):
        """Automatically paste the text after transcription (like in mic_test.py)"""
        try:
            # Use ctrl+v to paste - exactly like in mic_test.py
            keyboard.press_and_release('ctrl+v')
            self.status_var.set("Text auto-pasted")
            logger.info("Text auto-pasted successfully")
        except Exception as e:
            error_msg = f"Error auto-pasting: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.status_var.set(error_msg)
    
    def clear_transcription(self):
        self.transcription = ""
        self.update_transcription_text()
        self.status_var.set("Transcription cleared")
        
    def handle_callback_error(self, exc_type, exc_value, exc_traceback):
        """Handle exceptions in tkinter callbacks"""
        error_msg = f"Error in GUI callback: {exc_value}"
        logger.error(error_msg)
        logger.error("Exception details:", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Show error message but don't crash
        self.status_var.set(error_msg)
        messagebox.showerror("Error", f"An error occurred: {exc_value}\n\nThe application will continue running.")
        
        # Try to recover from the error
        try:
            # Re-enable buttons that might have been disabled
            self.record_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.paste_button.configure(state="normal")
            
            # Reset recording state
            self.recording = False
            self.stop_recording.set()
            
            # Clean up any resources
            if hasattr(self, 'recording_thread') and self.recording_thread and self.recording_thread.is_alive():
                # Can't really stop the thread, but we can set the flag
                self.stop_recording.set()
        except Exception as e:
            logger.error(f"Error during recovery: {str(e)}")
            pass
    
    def on_closing(self):
        logger.info("Application closing, cleaning up resources")
        # Clean up resources
        try:
            keyboard.unhook_all()
            logger.debug("Keyboard hooks unhooked")
            
            if hasattr(self, 'p'):
                self.p.terminate()
                logger.debug("PyAudio terminated")
                
            logger.info("Application shutdown complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            
        self.root.destroy()

def main():
    try:
        logger.info("Starting Whisper GUI application")
        root = tk.Tk()
        
        # Set up exception handler for unhandled exceptions
        def handle_exception(exc_type, exc_value, exc_traceback):
            logger.critical("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))
            messagebox.showerror("Critical Error", 
                               f"Application encountered an error: {exc_value}\n\n"
                               f"The application will attempt to restart automatically.")
            
            # Force close the application and let the wrapper script restart it
            os._exit(1)
        
        # Install exception handler
        sys.excepthook = handle_exception
        
        app = WhisperGUI(root)
        logger.info("GUI initialized, entering main loop")
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"Fatal error in main: {str(e)}")
        logger.critical(traceback.format_exc())
        messagebox.showerror("Critical Error", 
                           f"Application crashed: {str(e)}\n\n"
                           f"The application will attempt to restart automatically.")
        
        # Exit with error code so the wrapper script can restart
        sys.exit(1)

if __name__ == "__main__":
    main()
