import os
import subprocess
import re
from pathlib import Path

# Configuration
REMOTE_NAME = "small"
BASE_REMOTE_PATH = "small/image"
LOCAL_PATH = r"C:\huang\Image-1"

# Color codes for terminal output
class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"
    RESET = "\033[0m"

def print_color(message, color=Colors.RESET):
    print(f"{color}{message}{Colors.RESET}")

def convert_folder_name(folder_name):
    """Convert folder name (keep original)"""
    return folder_name

def test_remote_directory_exists(remote_dirs, target_dir):
    """Check if remote directory exists"""
    return target_dir in remote_dirs

def get_remote_directories(remote_path):
    """Get R2 remote directory list"""
    print_color(f"Getting remote directory list: {remote_path}...", Colors.YELLOW)
    
    try:
        result = subprocess.run(
            ['rclone', 'lsd', f'{REMOTE_NAME}:{remote_path}'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            shell=True
        )
        
        if result.returncode != 0:
            print_color("Warning: Cannot get remote directory list", Colors.YELLOW)
            return []
        
        dirs = []
        pattern = r'\s+(-?\d+)\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+(-?\d+)\s+(.+)$'
        
        for line in result.stdout.split('\n'):
            match = re.match(pattern, line)
            if match:
                dir_name = match.group(3).strip()
                dirs.append(dir_name)
        
        return dirs
    except Exception as e:
        print_color(f"Error: Failed to get remote directory list - {str(e)}", Colors.RED)
        return []

def test_local_directory(dir_path):
    """Check if local directory exists"""
    return os.path.isdir(dir_path)

def upload_directory(local_dir, remote_dir):
    """Upload directory to R2"""
    local_full_path = os.path.join(LOCAL_PATH, local_dir)
    remote_full_path = f"{BASE_REMOTE_PATH}/{remote_dir}"
    
    print_color("", Colors.RESET)
    print_color("----------------------------------------", Colors.GREEN)
    print_color(f"Uploading: {local_dir} -> {remote_dir}", Colors.GREEN)
    print_color("----------------------------------------", Colors.GREEN)
    
    try:
        result = subprocess.run(
            ['rclone', 'copy', local_full_path, f'{REMOTE_NAME}:{remote_full_path}', '--progress'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            shell=True
        )
        
        if result.returncode == 0:
            print_color(f"[OK] Upload success: {local_dir}", Colors.GREEN)
            return True
        else:
            print_color(f"[FAIL] Upload failed: {local_dir}", Colors.RED)
            return False
    except Exception as e:
        print_color(f"[ERROR] Upload exception: {local_dir} - {str(e)}", Colors.RED)
        return False

def main():
    try:
        print_color("========================================", Colors.CYAN)
        print_color("R2 Auto Upload Script", Colors.CYAN)
        print_color("========================================", Colors.CYAN)
        print_color("", Colors.RESET)
        
        # Get existing remote directories
        print_color("Step 1: Checking R2 remote directories...", Colors.CYAN)
        remote_dirs = get_remote_directories(BASE_REMOTE_PATH)
        print_color(f"Remote existing directories: {', '.join(remote_dirs)}", Colors.GRAY)
        print_color("", Colors.RESET)
        
        # Get all local subdirectories
        print_color("Step 2: Scanning local directories...", Colors.CYAN)
        local_path_obj = Path(LOCAL_PATH)
        
        # Filter out script files and conversion record
        excluded_names = {'conversion_record.json', 'upload_to_r2.ps1', 'upload_to_r2.py', 'convert_to_webp.py', 'convert_to_webp.bat'}
        local_dirs = [d for d in local_path_obj.iterdir() if d.is_dir() and d.name not in excluded_names]
        
        print_color(f"Found {len(local_dirs)} local directories", Colors.GRAY)
        print_color("", Colors.RESET)
        
        # Check and upload each folder
        upload_count = 0
        skip_count = 0
        fail_count = 0
        
        for dir_path in local_dirs:
            local_dir_name = dir_path.name
            remote_dir_name = convert_folder_name(local_dir_name)
            
            print_color(f"Checking folder: {local_dir_name} (remote name: {remote_dir_name})", Colors.CYAN)
            
            # Check if local directory exists
            local_full_path = os.path.join(LOCAL_PATH, local_dir_name)
            if not test_local_directory(local_full_path):
                print_color(f"  [SKIP] Local directory not found: {local_dir_name}", Colors.YELLOW)
                skip_count += 1
                continue
            
            # Check if remote directory already exists
            if test_remote_directory_exists(remote_dirs, remote_dir_name):
                print_color(f"  [SKIP] Remote directory already exists: {remote_dir_name}", Colors.YELLOW)
                skip_count += 1
                continue
            
            # Upload directory
            success = upload_directory(local_dir_name, remote_dir_name)
            if success:
                upload_count += 1
            else:
                fail_count += 1
        
        # Output summary
        print_color("", Colors.RESET)
        print_color("========================================", Colors.CYAN)
        print_color("Upload Complete!", Colors.CYAN)
        print_color("========================================", Colors.CYAN)
        print_color(f"Successfully uploaded: {upload_count} folders", Colors.GREEN)
        print_color(f"Skipped (already exists): {skip_count} folders", Colors.YELLOW)
        print_color(f"Failed: {fail_count} folders", Colors.RED)
        print_color("", Colors.RESET)
        
        # Display current remote directory status
        print_color("Current remote directory list:", Colors.CYAN)
        final_remote_dirs = get_remote_directories(BASE_REMOTE_PATH)
        for dir_name in final_remote_dirs:
            print_color(f"  - {dir_name}", Colors.GRAY)
        
    except Exception as e:
        print_color("", Colors.RESET)
        print_color(f"[ERROR] Script execution failed: {str(e)}", Colors.RED)
        exit(1)

if __name__ == "__main__":
    main()
