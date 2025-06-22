import sys

try:
    import faster_whisper
    print("faster_whisper imported successfully")
    sys.exit(0)
except ImportError as e:
    print(f"Failed to import faster_whisper: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
