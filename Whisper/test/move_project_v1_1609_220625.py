import os
import shutil
from datetime import datetime

try:
    # Create directories
    os.makedirs("F:\\Code\\Whisper\\src", exist_ok=True)
    os.makedirs("F:\\Code\\Whisper\\test", exist_ok=True)
    os.makedirs("F:\\Code\\Whisper\\logs", exist_ok=True)
    
    # Move files from e:\whisper_test
    src_dir = "e:\\whisper_test"
    dest_dir = "F:\\Code\\Whisper\\src"
    
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        if os.path.isfile(src_path):
            # Create versioned backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.splitext(item)[0]}_backup_v1_{timestamp}.py"
            shutil.copy2(src_path, os.path.join("F:\\Code\\Whisper\\test", backup_name))
            
            # Move to src
            shutil.move(src_path, os.path.join(dest_dir, item))
    
    print("Project moved successfully")
except Exception as e:
    print(f"Error moving project: {e}")
    sys.exit(1)
