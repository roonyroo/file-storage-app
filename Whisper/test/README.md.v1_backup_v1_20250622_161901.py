# Faster-Whisper Voice-to-Text Tool

A simple voice-to-text tool using Faster-Whisper for speech recognition.

## Features

- Press backtick (`) key to start recording
- Press Caps Lock to stop recording
- Transcription copied to clipboard automatically
- Automatic pasting of transcription
- Continuous operation mode
- Uses the "small" Whisper model for good accuracy

## Requirements

- Python 3.x
- PyAudio
- faster-whisper
- keyboard
- pyperclip

## Installation

All required packages should already be installed. If not, you can install them with:

```
pip install faster-whisper pyaudio keyboard pyperclip
```

## Usage

1. Run the script: `python mic_test.py`
2. Press the backtick key (`) to start recording
3. Speak your message
4. Press Caps Lock when you're done speaking
5. The script will transcribe your speech and copy it to clipboard
6. Switch to your target application within 2 seconds
7. The text will be automatically pasted
8. The script will restart automatically for the next recording

## Models

Faster-Whisper supports different model sizes:
- `tiny`: Smallest and fastest, less accurate
- `base`: Good balance of speed and accuracy
- `small`: Better accuracy, slower
- `medium`: Even better accuracy, even slower
- `large-v2`: Most accurate, slowest

To change the model, edit the `mic_test.py` file and change the model parameter:
```python
model = WhisperModel("tiny", device="cpu", compute_type="int8")
```

## Troubleshooting

If you encounter issues with PyAudio:
1. Make sure your microphone is properly connected
2. Check your system's audio input settings
3. Try reinstalling PyAudio: `pip install --force-reinstall pyaudio`
