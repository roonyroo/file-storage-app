import os
import shutil
from datetime import datetime

# Source and destination
src_dir = "e:\\whisper_test"
dest_dir = "F:\\Code\\Whisper\\src"

# Create versioned backups first
try:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        if os.path.isfile(src_path):
            # Create backup
            backup_path = os.path.join("F:\\Code\\Whisper\\test", f"{item}_backup_v1_{timestamp}.py")
            shutil.copy2(src_path, backup_path)
            
            # Move to src
            shutil.move(src_path, os.path.join(dest_dir, item))
    
    print("Files moved successfully with backups created")
except Exception as e:
    print(f"Error moving files: {e}")
    sys.exit(1)
