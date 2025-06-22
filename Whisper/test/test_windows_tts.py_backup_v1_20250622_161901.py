"""
Simple Windows TTS test using win32com.client
This should work without additional packages on Windows
"""

try:
    import win32com.client
    
    def test_windows_tts():
        print("Testing Windows SAPI text-to-speech...")
        try:
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            
            # List available voices
            voices = speaker.GetVoices()
            print(f"Found {voices.Count} voices:")
            
            for i in range(voices.Count):
                voice = voices.Item(i)
                desc = voice.GetDescription()
                print(f"{i+1}. {desc}")
            
            # Use default voice
            print("\nUsing default voice")
            
            # Test speaking
            test_text = "This is a test of Windows SAPI text to speech. If you can hear this, the system is working correctly."
            print(f"Speaking: '{test_text}'")
            speaker.Speak(test_text)
            print("Speech completed")
            
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    if __name__ == "__main__":
        test_windows_tts()
        
except ImportError:
    print("win32com.client not available. Please install pywin32 with: pip install pywin32")
