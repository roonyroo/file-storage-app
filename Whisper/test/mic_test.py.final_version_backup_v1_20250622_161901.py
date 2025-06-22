import os
import tempfile
import wave
import pyaudio
import time
import numpy as np
import threading
import keyboard
import pyperclip
import sys
from faster_whisper import WhisperModel

def calibrate_microphone(sample_rate=16000, duration=3):
    """Calibrate microphone by measuring ambient noise level."""
    print("\nCalibrating microphone - please stay silent for 3 seconds...")
    
    # PyAudio setup
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=1024)
    
    # Collect volume levels
    volumes = []
    for i in range(0, int(sample_rate / 1024 * duration)):
        data = stream.read(1024, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        volume = np.abs(audio_data).mean()
        volumes.append(volume)
        
        # Print progress
        if i % 10 == 0:
            print(".", end="", flush=True)
    
    # Close stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Calculate threshold (mean + 2 standard deviations)
    ambient_level = np.mean(volumes)
    threshold = ambient_level * 1.5  # 50% above ambient noise
    
    print(f"\nCalibration complete!")
    print(f"Ambient noise level: {ambient_level:.2f}")
    print(f"Speech detection threshold: {threshold:.2f}")
    
    return threshold

def record_audio_with_hotkeys(sample_rate=16000):
    """Record audio when backtick is pressed and stop when Caps Lock is pressed."""
    print("Press BACKTICK (`) key to start recording")
    print("Press CAPS LOCK to stop recording when finished speaking")
    
    # PyAudio setup
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=1024)
    
    # Variables for recording
    frames = []
    recording = False
    recording_started = threading.Event()
    recording_stopped = threading.Event()
    
    # For visual audio level display
    max_bar_length = 50
    last_level_display_time = time.time()
    
    # Set up hotkey handlers
    def on_backtick_press(e):
        if e.name == '`' and e.event_type == keyboard.KEY_DOWN and not recording_started.is_set():
            recording_started.set()
            print("\nBACKTICK detected! Starting recording...")
            # Block the backtick from being typed
            return False  # This prevents the backtick character from being typed
    
    def on_caps_lock_press(e):
        if e.name == 'caps lock' and e.event_type == keyboard.KEY_DOWN and recording_started.is_set():
            recording_stopped.set()
            print("\nCAPS LOCK detected! Stopping recording...")
            return False  # Stop listening for this key
    
    # Register the global hotkeys
    keyboard.hook(on_backtick_press)
    keyboard.hook(on_caps_lock_press)
    
    try:
        # Wait for backtick to start recording
        print("Waiting for BACKTICK key press to start recording...")
        while not recording_started.is_set() and not recording_stopped.is_set():
            time.sleep(0.1)
        
        if recording_stopped.is_set():
            return None
        
        # Start recording
        recording = True
        print("\nRecording started! Press CAPS LOCK when finished.")
        
        # Main recording loop
        while recording and not recording_stopped.is_set():
            # Read audio data
            data = stream.read(1024, exception_on_overflow=False)
            
            # Convert to numpy array for analysis
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.abs(audio_data).mean()
            
            # Display audio level every 0.5 seconds
            current_time = time.time()
            if current_time - last_level_display_time > 0.5:
                # Create a visual bar representing volume level
                bar_length = min(int(volume / max_bar_length * 20), max_bar_length)
                bar = "█" * bar_length + "░" * (max_bar_length - bar_length)
                print(f"\rRecording: {bar} {len(frames)//32}s", end="", flush=True)
                last_level_display_time = current_time
            
            # Add the frame to our recording
            frames.append(data)
    
    except KeyboardInterrupt:
        print("\nRecording stopped by user")
    
    finally:
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Unhook keyboard listener
        keyboard.unhook_all()
        
        if len(frames) == 0:
            print("No audio was recorded!")
            return None
        
        print("\nRecording finished!")
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        
        # Save as WAV file
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))
        
        print(f"Audio saved to {temp_file.name}")
        return temp_file.name

def transcribe_audio(audio_path):
    """Transcribe audio file using Faster-Whisper and copy to clipboard."""
    if not audio_path:
        return ""
        
    print("Loading Faster-Whisper model (this may take a moment)...")
    
    # Load the small model (good balance between speed and accuracy)
    print("Loading small model (good balance between speed and accuracy)...")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    
    print("Transcribing audio...")
    # Transcribe the audio
    segments, info = model.transcribe(audio_path, beam_size=5)
    
    # Print transcription results
    print("\n--- Transcription Results ---")
    print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
    
    full_text = ""
    for segment in segments:
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
        full_text += segment.text + " "
    
    full_text = full_text.strip()
    print("\nFull transcription:", full_text)
    
    # Copy to clipboard
    pyperclip.copy(full_text)
    print("\nTranscription copied to clipboard!")
    
    # Automatically paste the text
    print("Auto-pasting text in 2 seconds... (Switch to your target window)")
    time.sleep(2)  # Give user time to switch windows
    keyboard.press_and_release('ctrl+v')
    print("Text pasted!")
    
    return full_text

def main():
    print("=== Faster-Whisper Auto Speech Detection ===")
    print("This script will automatically detect when you start speaking")
    print("and transcribe your speech when you press CAPS LOCK.")
    
    # Install keyboard if not already installed
    try:
        import keyboard
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "keyboard", "pyperclip"])
        import keyboard
        import pyperclip
    
    while True:
        try:
            # Record audio using hotkeys
            audio_path = record_audio_with_hotkeys()
            
            if audio_path:
                # Transcribe the recorded audio
                transcribe_audio(audio_path)
                
                # Clean up temporary file
                print(f"\nCleaning up temporary file: {audio_path}")
                os.remove(audio_path)
            
            # Brief pause before restarting
            print("\nRestarting in 3 seconds... (Press Ctrl+C to exit)")
            time.sleep(3)
                
        except KeyboardInterrupt:
            print("\nProgram interrupted by user.")
            break
    
    print("Done!")

if __name__ == "__main__":
    import sys
    main()
