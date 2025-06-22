try:
    import pyaudio
    print("Pyaudio imported successfully")
    sys.exit(0)
except ImportError as e:
    print(f"Failed to import pyaudio: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
