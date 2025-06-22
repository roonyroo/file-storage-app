import pyttsx3

def test_julie_voice():
    print("Testing TTS with pyttsx3...")
    engine = pyttsx3.init()
    
    # List all available voices
    voices = engine.getProperty('voices')
    print(f"Found {len(voices)} voices:")
    
    julie_voice = None
    for i, voice in enumerate(voices):
        print(f"{i+1}. {voice.name} | ID: {voice.id}")
        if 'julie' in voice.name.lower() or 'voiceware' in voice.id.lower():
            julie_voice = voice
    
    # Try to use Julie voice if available, otherwise use default
    if julie_voice:
        print(f"\nUsing Julie voice: {julie_voice.name}")
        engine.setProperty('voice', julie_voice.id)
    else:
        print("\nJulie voice not found, using default voice")
    
    # Test speaking
    test_text = "This is a test of text to speech using pyttsx3. If you can hear this, the system is working correctly."
    print(f"Speaking: '{test_text}'")
    engine.say(test_text)
    engine.runAndWait()
    print("Speech completed")

if __name__ == "__main__":
    test_julie_voice()
