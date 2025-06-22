"""
Julie Voice Verification and Test Script
This script checks if the Julie voice is registered and tests it
"""

import os
import sys
import time
import winreg
import pyttsx3
import traceback

# Configuration
JULIE_DLL_PATH = r"C:\Program Files (x86)\VW\VT\Julie\M16-SAPI5\lib\vt_eng_julie16.dll"
JULIE_REGISTRY_PATH = r"SOFTWARE\Microsoft\Speech\Voices\Tokens\VW Julie"
TRANSCRIPTION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcriptions.txt")

def check_julie_registry():
    """Check if Julie voice is registered in the Windows registry"""
    print("=== Julie Voice Registry Check ===")
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, JULIE_REGISTRY_PATH)
        clsid = winreg.QueryValueEx(key, "CLSID")[0]
        print(f"SUCCESS: Julie voice found in registry")
        print(f"CLSID: {clsid}")
        return True
    except Exception as e:
        print(f"ERROR: Julie voice not found in registry: {str(e)}")
        print(f"\nTo register the Julie voice, run this command as Administrator:")
        print(f'regsvr32 "{JULIE_DLL_PATH}"')
        return False

def list_available_voices():
    """List all available TTS voices on the system"""
    print("\n=== Available TTS Voices ===")
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print(f"Found {len(voices)} voices:")
        for i, voice in enumerate(voices):
            print(f"{i+1}. {voice.name} | ID: {voice.id}")
        
        return voices
    except Exception as e:
        print(f"ERROR listing voices: {str(e)}")
        return []

def test_julie_voice():
    """Test the Julie voice if available"""
    print("\n=== Julie Voice Test ===")
    try:
        engine = pyttsx3.init()
        
        # Try to set Julie voice using registry path
        julie_voice_path = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\VW Julie"
        engine.setProperty('voice', julie_voice_path)
        
        # Verify the voice was set
        current_voice = engine.getProperty('voice')
        print(f"Current voice: {current_voice}")
        
        # Test speech
        test_text = "This is a test of the Julie voice. If you can hear this, the voice is working correctly."
        print(f"Speaking: '{test_text}'")
        engine.say(test_text)
        engine.runAndWait()
        print("Speech completed")
        return True
    except Exception as e:
        print(f"ERROR testing Julie voice: {str(e)}")
        traceback.print_exc()
        return False

def test_default_voice():
    """Test the default system voice"""
    print("\n=== Default Voice Test ===")
    try:
        engine = pyttsx3.init()
        
        # Get current voice
        current_voice = engine.getProperty('voice')
        print(f"Default voice: {current_voice}")
        
        # Test speech
        test_text = "This is a test of the default system voice. If you can hear this, text-to-speech is working correctly."
        print(f"Speaking: '{test_text}'")
        engine.say(test_text)
        engine.runAndWait()
        print("Speech completed")
        return True
    except Exception as e:
        print(f"ERROR testing default voice: {str(e)}")
        return False

def monitor_transcriptions():
    """Monitor the transcriptions.txt file and speak new text"""
    print("\n=== Monitoring Transcriptions ===")
    print(f"Watching file: {TRANSCRIPTION_FILE}")
    
    # Create file if it doesn't exist
    if not os.path.exists(TRANSCRIPTION_FILE):
        with open(TRANSCRIPTION_FILE, 'w', encoding='utf-8') as f:
            pass
        print(f"Created empty transcription file")
    
    # Initialize TTS engine
    try:
        engine = pyttsx3.init()
        
        # Try to use Julie voice if available
        try:
            julie_voice_path = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\VW Julie"
            engine.setProperty('voice', julie_voice_path)
            print("Using Julie voice for transcriptions")
        except:
            print("Using default voice for transcriptions")
        
        # Track last read position
        last_size = os.path.getsize(TRANSCRIPTION_FILE)
        
        print("Monitoring for new transcriptions (press Ctrl+C to stop)...")
        while True:
            try:
                # Check if file has new content
                current_size = os.path.getsize(TRANSCRIPTION_FILE)
                
                if current_size > last_size:
                    # Read new content
                    with open(TRANSCRIPTION_FILE, 'r', encoding='utf-8') as f:
                        f.seek(last_size)
                        new_text = f.read().strip()
                    
                    if new_text:
                        print(f"New transcription: {new_text}")
                        engine.say(new_text)
                        engine.runAndWait()
                    
                    last_size = current_size
                
                # Sleep before checking again
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print(f"Error during monitoring: {str(e)}")
                time.sleep(1)
    
    except Exception as e:
        print(f"ERROR setting up monitoring: {str(e)}")

if __name__ == "__main__":
    print("=== Julie Voice Verification and Test ===")
    
    # Check registry
    julie_registered = check_julie_registry()
    
    # List available voices
    voices = list_available_voices()
    
    # Test voices
    if julie_registered:
        test_julie_voice()
    else:
        test_default_voice()
    
    # Ask if user wants to monitor transcriptions
    print("\n=== Transcription Monitoring ===")
    response = input("Do you want to monitor transcriptions.txt for text-to-speech? (y/n): ")
    
    if response.lower() == 'y':
        monitor_transcriptions()
    else:
        print("Exiting without monitoring transcriptions")
