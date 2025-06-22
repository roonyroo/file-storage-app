import os
import shutil

# Move files back from src to original location
try:
    src_dir = "F:\\Code\\Whisper\\src"
    dest_dir = "e:\\whisper_test"
    
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        if os.path.isfile(src_path):
            shutil.move(src_path, os.path.join(dest_dir, item))
    
    print("Files restored successfully")
except Exception as e:
    print(f"Error restoring files: {e}")
    sys.exit(1)
