"""
Julie Voice Registration Fix Script
This script helps diagnose and fix Julie voice registration issues
"""

import os
import sys
import subprocess
import winreg
import ctypes
import platform

# Configuration
JULIE_DLL_PATH = r"C:\Program Files (x86)\VW\VT\Julie\M16-SAPI5\lib\vt_eng_julie16.dll"
JULIE_REGISTRY_PATH = r"SOFTWARE\Microsoft\Speech\Voices\Tokens\VW Julie"

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_dll_exists():
    """Check if the Julie DLL file exists"""
    print(f"Checking if DLL exists: {JULIE_DLL_PATH}")
    if os.path.exists(JULIE_DLL_PATH):
        print(f"SUCCESS: DLL file found")
        return True
    else:
        print(f"ERROR: DLL file not found")
        return False

def check_dll_architecture():
    """Check the architecture of the DLL file"""
    print(f"Checking DLL architecture...")
    try:
        # This is a simple check - not 100% reliable but gives an indication
        with open(JULIE_DLL_PATH, 'rb') as f:
            dos_header = f.read(2)
            if dos_header == b'MZ':
                print("File appears to be a valid PE executable")
                
                # Skip to PE header offset
                f.seek(60)
                pe_offset = int.from_bytes(f.read(4), byteorder='little')
                f.seek(pe_offset)
                
                # Check PE signature
                pe_sig = f.read(4)
                if pe_sig == b'PE\x00\x00':
                    # Read machine type
                    f.seek(pe_offset + 4)
                    machine_type = int.from_bytes(f.read(2), byteorder='little')
                    
                    if machine_type == 0x014c:
                        print("DLL is 32-bit (x86)")
                        return "32-bit"
                    elif machine_type == 0x8664:
                        print("DLL is 64-bit (x64)")
                        return "64-bit"
                    else:
                        print(f"Unknown machine type: {hex(machine_type)}")
                        return "unknown"
                else:
                    print("Invalid PE signature")
                    return "unknown"
            else:
                print("Not a valid PE file")
                return "unknown"
    except Exception as e:
        print(f"Error checking DLL architecture: {str(e)}")
        return "unknown"

def check_system_architecture():
    """Check the system architecture"""
    print(f"Checking system architecture...")
    arch = platform.architecture()[0]
    print(f"System architecture: {arch}")
    return arch

def check_julie_registry():
    """Check if Julie voice is registered in the Windows registry"""
    print(f"Checking registry entry: {JULIE_REGISTRY_PATH}")
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, JULIE_REGISTRY_PATH)
        clsid = winreg.QueryValueEx(key, "CLSID")[0]
        print(f"SUCCESS: Julie voice found in registry")
        print(f"CLSID: {clsid}")
        return True
    except Exception as e:
        print(f"ERROR: Julie voice not found in registry: {str(e)}")
        return False

def register_dll():
    """Attempt to register the DLL with the correct architecture"""
    print(f"Attempting to register DLL: {JULIE_DLL_PATH}")
    
    if not is_admin():
        print("ERROR: This script must be run as Administrator to register DLLs")
        print("Please restart this script with Administrator privileges")
        return False
    
    dll_arch = check_dll_architecture()
    sys_arch = check_system_architecture()
    
    # Determine which regsvr32 to use
    if dll_arch == "32-bit":
        if sys_arch == "64bit":
            # Use 32-bit regsvr32 on 64-bit system
            regsvr32_path = r"C:\Windows\SysWOW64\regsvr32.exe"
        else:
            # Use regular regsvr32 on 32-bit system
            regsvr32_path = r"C:\Windows\System32\regsvr32.exe"
    else:
        # Use regular regsvr32
        regsvr32_path = r"C:\Windows\System32\regsvr32.exe"
    
    print(f"Using regsvr32 from: {regsvr32_path}")
    
    try:
        # Run regsvr32 with the DLL path
        result = subprocess.run([regsvr32_path, JULIE_DLL_PATH], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS: DLL registered successfully")
            return True
        else:
            print(f"ERROR: Failed to register DLL")
            print(f"Return code: {result.returncode}")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"ERROR: Exception while registering DLL: {str(e)}")
        return False

def check_dependencies():
    """Check for common dependencies"""
    print("Checking for common dependencies...")
    dependencies = [
        r"C:\Windows\System32\msvcr100.dll",
        r"C:\Windows\System32\msvcp100.dll",
        r"C:\Windows\SysWOW64\msvcr100.dll",
        r"C:\Windows\SysWOW64\msvcp100.dll"
    ]
    
    missing = []
    for dep in dependencies:
        if not os.path.exists(dep):
            missing.append(dep)
            print(f"Missing dependency: {dep}")
        else:
            print(f"Found dependency: {dep}")
    
    if missing:
        print("\nSome dependencies are missing. You may need to install:")
        print("- Microsoft Visual C++ 2010 Redistributable Package")
        return False
    else:
        print("All common dependencies found")
        return True

def main():
    """Main function to diagnose and fix Julie voice issues"""
    print("=== Julie Voice Registration Fix ===\n")
    
    # Check if running as admin
    if not is_admin():
        print("WARNING: This script is not running as Administrator")
        print("Some operations may fail without admin privileges")
        print("Please restart this script with Administrator privileges\n")
    
    # Check if DLL exists
    if not check_dll_exists():
        print("\nThe Julie voice DLL was not found at the expected location.")
        print("Please make sure the Julie voice is installed correctly.")
        return
    
    # Check DLL and system architecture
    dll_arch = check_dll_architecture()
    sys_arch = check_system_architecture()
    print(f"DLL architecture: {dll_arch}")
    print(f"System architecture: {sys_arch}")
    
    # Check dependencies
    check_dependencies()
    
    # Check if already registered
    julie_registered = check_julie_registry()
    
    if julie_registered:
        print("\nThe Julie voice appears to be properly registered.")
        print("If you're still having issues, try using the correct regsvr32 for your architecture:")
        print(f"32-bit: C:\\Windows\\SysWOW64\\regsvr32.exe \"{JULIE_DLL_PATH}\"")
        print(f"64-bit: C:\\Windows\\System32\\regsvr32.exe \"{JULIE_DLL_PATH}\"")
    else:
        print("\nThe Julie voice is not properly registered.")
        
        if is_admin():
            print("Attempting to register the DLL...")
            register_dll()
        else:
            print("Please run these commands as Administrator to register the DLL:")
            print(f"32-bit: C:\\Windows\\SysWOW64\\regsvr32.exe \"{JULIE_DLL_PATH}\"")
            print(f"64-bit: C:\\Windows\\System32\\regsvr32.exe \"{JULIE_DLL_PATH}\"")

if __name__ == "__main__":
    main()
    print("\nPress Enter to exit...")
    input()
