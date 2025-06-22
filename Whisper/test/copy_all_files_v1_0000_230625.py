import os
import shutil
import datetime

# Source and destination paths
src_dir = r"e:\whisper_test"
dst_dir = r"F:\Code\Whisper"

# Get timestamp for versioned files
timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M")

def copy_files():
    try:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(dst_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Copy all files (excluding logs directory which we'll handle separately)
        for item in os.listdir(src_dir):
            src_path = os.path.join(src_dir, item)
            dst_path = os.path.join(dst_dir, item)
            
            # Handle log directory separately
            if item == "logs" and os.path.isdir(src_path):
                print(f"Creating logs directory: {logs_dir}")
                continue
                
            # Copy files and directories
            if os.path.isfile(src_path):
                print(f"Copying file: {item}")
                shutil.copy2(src_path, dst_path)
            elif os.path.isdir(src_path) and item != "logs":
                print(f"Copying directory: {item}")
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                
        print("File copy completed successfully")
        return True
    except Exception as e:
        print(f"Error copying files: {str(e)}")
        return False

if __name__ == "__main__":
    copy_files()
