# Whisper Speech-to-Text Tool

This tool uses Faster-Whisper to transcribe speech from your microphone to text.

## Features

- Uses the backtick key (`) to start recording
- Uses Caps Lock key to stop recording
- Automatically copies transcription to clipboard
- Automatically pastes transcription after copying (2-second delay)
- Continuous operation mode (restarts listening after each transcription)
- GUI version with language selection
- Auto-restart capability if the application crashes
- Comprehensive error handling and logging

## Requirements

- Python 3.8+
- faster-whisper
- pyaudio
- numpy
- keyboard
- pyperclip
- tkinter (for GUI version)

## Usage - Command Line Version

1. Run the script: `python mic_test.py`
2. Press the backtick key (`) to start recording
3. Speak into your microphone
4. Press Caps Lock to stop recording
5. The transcription will be automatically copied to clipboard and pasted

## Usage - GUI Version

1. Run the launcher script: `python run_whisper_gui.py`
2. Select your preferred language (English, Urdu, Hindi, Bengali, Punjabi)
3. Select the model size (tiny, base, small, medium)
4. Press the backtick key (`) or click "Start Recording" to begin
5. Speak into your microphone
6. Press Caps Lock or click "Stop Recording" to stop
7. The transcription will appear in the text area and be copied to clipboard
8. The text will be automatically pasted after a 2-second delay
9. You can also click "Paste" to manually paste the text

## Model Selection

The script uses the "small" model by default, which provides a good balance between accuracy and speed on CPU. You can change this in the GUI or by modifying the model parameter in the script.

Available models:
- tiny (fastest, least accurate)
- base
- small (good balance)
- medium (more accurate but slower)
- large (most accurate, requires more resources)

## Languages

The GUI version supports the following languages:
- English
- Urdu
- Hindi
- Bengali
- Punjabi

## Error Handling

The application includes comprehensive error handling and logging:
- Logs are stored in the `logs` directory
- The launcher script automatically restarts the application if it crashes
- View logs button in the GUI for easy access to log files

## Files

- `mic_test.py` - Command line version
- `whisper_gui.py` - GUI version
- `run_whisper_gui.py` - Launcher script with auto-restart capability

## Troubleshooting

If you encounter issues with PyAudio:
1. Make sure your microphone is properly connected
2. Check your system's audio input settings
3. Try reinstalling PyAudio: `pip install --force-reinstall pyaudio`

If the application crashes:
1. Check the logs in the `logs` directory
2. The launcher script should automatically restart the application
3. If it doesn't restart, run `python run_whisper_gui.py` again
