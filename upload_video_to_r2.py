#!/usr/bin/env python3
"""
视频上传R2脚本
将video-1文件夹中的视频上传到R2的small/video目录下
"""
import os
import subprocess
import re
import json
from pathlib import Path

# 配置
REMOTE_NAME = "small"
BASE_REMOTE_PATH = "small/video"
LOCAL_PATH = r"C:\huang\video-1"
UPLOAD_RECORD_FILE = r"C:\huang\video_upload_record.json"

# 终端颜色代码
class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"
    RESET = "\033[0m"

def print_color(message, color=Colors.RESET):
    print(f"{color}{message}{Colors.RESET}")

def load_upload_record(json_path):
    """加载上传记录JSON文件"""
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告: 无法读取上传记录文件: {str(e)}")
            return {"uploaded_posts": {}}
    return {"uploaded_posts": {}}

def save_upload_record(json_path, record):
    """保存上传记录到JSON文件"""
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"警告: 无法保存上传记录文件: {str(e)}")

def is_post_uploaded(record, group_name, post_title):
    """检查博文是否已上传"""
    key = f"{group_name}/{post_title}"
    return key in record.get("uploaded_posts", {})

def add_upload_record(record, group_name, post_title):
    """添加上传记录"""
    key = f"{group_name}/{post_title}"
    record["uploaded_posts"][key] = {
        "group_name": group_name,
        "post_title": post_title,
        "timestamp": os.path.getmtime(os.path.join(LOCAL_PATH, group_name, post_title))
    }

def convert_folder_name(folder_name):
    """转换文件夹名称（保持原样）"""
    return folder_name

def get_remote_directories(remote_path):
    """获取R2远程目录列表"""
    print_color(f"获取远程目录列表: {remote_path}...", Colors.YELLOW)
    
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
            print_color("警告: 无法获取远程目录列表", Colors.YELLOW)
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
        print_color(f"错误: 获取远程目录列表失败 - {str(e)}", Colors.RED)
        return []

def test_local_directory(dir_path):
    """检查本地目录是否存在"""
    return os.path.isdir(dir_path)

def get_mime_type(file_path):
    """根据文件扩展名获取MIME类型"""
    ext = os.path.splitext(file_path)[1].lower()
    mime_types = {
        '.m3u8': 'application/vnd.apple.mpegurl',
        '.ts': 'video/mp2t',
        '.json': 'application/json',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
    }
    return mime_types.get(ext, None)

def upload_file_with_mime(local_file, remote_path):
    """上传单个文件并设置正确的MIME类型"""
    mime_type = get_mime_type(local_file)
    file_name = os.path.basename(local_file)
    
    # remote_path 是包含文件名的完整路径，需要提取目录部分
    remote_dir = os.path.dirname(remote_path)
    if not remote_dir:
        remote_dir = "."
    
    # 构建命令：rclone copy 本地文件 远程目录
    cmd = ['rclone', 'copy', local_file, f'{REMOTE_NAME}:{remote_dir}']
    
    # 添加MIME类型设置（使用 --header-upload）
    if mime_type:
        cmd.extend(['--header-upload', f'Content-Type: {mime_type}'])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            shell=True
        )
        if result.returncode != 0:
            print_color(f"[DEBUG] rclone错误: {result.stderr[:200]}", Colors.GRAY)
        return result.returncode == 0
    except Exception as e:
        print_color(f"[ERROR] 上传文件失败: {local_file} - {str(e)}", Colors.RED)
        return False

def upload_directory(local_dir, remote_dir):
    """上传目录到R2，并为HLS文件设置正确的MIME类型"""
    local_full_path = os.path.join(LOCAL_PATH, local_dir)
    remote_full_path = f"{BASE_REMOTE_PATH}/{remote_dir}"
    
    print_color("", Colors.RESET)
    print_color("----------------------------------------", Colors.GREEN)
    print_color(f"上传: {local_dir} -> {remote_dir}", Colors.GREEN)
    print_color("----------------------------------------", Colors.GREEN)
    
    try:
        # 遍历目录中的所有文件
        success_count = 0
        fail_count = 0
        
        for root, dirs, files in os.walk(local_full_path):
            for file in files:
                local_file = os.path.join(root, file)
                # 计算相对路径
                rel_path = os.path.relpath(local_file, local_full_path)
                # 将Windows路径分隔符替换为Unix风格
                rel_path_unix = rel_path.replace('\\', '/')
                remote_file_path = f"{remote_full_path}/{rel_path_unix}"
                
                # 上传文件并设置MIME类型
                if upload_file_with_mime(local_file, remote_file_path):
                    success_count += 1
                else:
                    fail_count += 1
                    print_color(f"[FAIL] 上传失败: {rel_path}", Colors.RED)
        
        if fail_count == 0:
            print_color(f"[OK] 上传成功: {local_dir} ({success_count} 个文件)", Colors.GREEN)
            return True
        else:
            print_color(f"[WARN] 部分上传失败: {success_count} 成功, {fail_count} 失败", Colors.YELLOW)
            return False
            
    except Exception as e:
        print_color(f"[ERROR] 上传异常: {local_dir} - {str(e)}", Colors.RED)
        return False

def main():
    try:
        print_color("========================================", Colors.CYAN)
        print_color("视频R2上传脚本", Colors.CYAN)
        print_color("========================================", Colors.CYAN)
        print_color("", Colors.RESET)
        
        # 加载上传记录
        record = load_upload_record(UPLOAD_RECORD_FILE)
        print(f"加载上传记录: {UPLOAD_RECORD_FILE}")
        print(f"已记录的上传数: {len(record.get('uploaded_posts', {}))}")
        print_color("", Colors.RESET)
        
        # 获取已存在的远程目录
        print_color("步骤1: 检查R2远程目录...", Colors.CYAN)
        remote_group_dirs = get_remote_directories(BASE_REMOTE_PATH)
        print_color(f"远程已存在的分组: {', '.join(remote_group_dirs)}", Colors.GRAY)
        print_color("", Colors.RESET)
        
        # 获取所有本地分组目录
        print_color("步骤2: 扫描本地目录...", Colors.CYAN)
        local_path_obj = Path(LOCAL_PATH)
        
        if not local_path_obj.exists():
            print_color(f"错误: 本地目录不存在: {LOCAL_PATH}", Colors.RED)
            return
        
        # 获取所有分组目录
        group_dirs = [d for d in local_path_obj.iterdir() if d.is_dir()]
        
        print_color(f"找到 {len(group_dirs)} 个视频分组", Colors.GRAY)
        print_color("", Colors.RESET)
        
        # 检查并上传每个分组下的博文
        upload_count = 0
        skip_count = 0
        fail_count = 0
        
        for group_dir in group_dirs:
            group_name = group_dir.name
            remote_group_name = convert_folder_name(group_name)
            
            print_color(f"处理视频分组: {group_name}", Colors.CYAN)
            
            # 获取该分组下的所有博文目录
            post_dirs = [d for d in group_dir.iterdir() if d.is_dir()]
            
            for post_dir in post_dirs:
                post_title = post_dir.name
                remote_post_title = convert_folder_name(post_title)
                
                local_post_path = f"{group_name}/{post_title}"
                remote_post_path = f"{remote_group_name}/{remote_post_title}"
                
                print_color(f"  检查博文: {post_title}", Colors.CYAN)
                
                # 检查是否已上传（通过记录文件）
                if is_post_uploaded(record, group_name, post_title):
                    print_color(f"    [SKIP] 已上传（记录）: {post_title}", Colors.YELLOW)
                    skip_count += 1
                    continue
                
                # 检查本地目录是否存在
                if not test_local_directory(str(post_dir)):
                    print_color(f"    [SKIP] 本地目录不存在: {post_title}", Colors.YELLOW)
                    skip_count += 1
                    continue
                
                # 上传目录
                local_relative_path = f"{group_name}/{post_title}"
                remote_relative_path = f"{remote_group_name}/{remote_post_title}"
                
                success = upload_directory(local_relative_path, remote_relative_path)
                if success:
                    add_upload_record(record, group_name, post_title)
                    upload_count += 1
                else:
                    fail_count += 1
        
        # 保存上传记录
        if upload_count > 0:
            save_upload_record(UPLOAD_RECORD_FILE, record)
        
        # 输出总结
        print_color("", Colors.RESET)
        print_color("========================================", Colors.CYAN)
        print_color("上传完成!", Colors.CYAN)
        print_color("========================================", Colors.CYAN)
        print_color(f"成功上传: {upload_count} 个博文", Colors.GREEN)
        print_color(f"跳过: {skip_count} 个博文", Colors.YELLOW)
        print_color(f"失败: {fail_count} 个博文", Colors.RED)
        print_color("", Colors.RESET)
        
        # 显示当前远程目录状态
        print_color("当前远程分组列表:", Colors.CYAN)
        final_remote_dirs = get_remote_directories(BASE_REMOTE_PATH)
        for dir_name in final_remote_dirs:
            print_color(f"  - {dir_name}", Colors.GRAY)
        
    except Exception as e:
        print_color("", Colors.RESET)
        print_color(f"[ERROR] 脚本执行失败: {str(e)}", Colors.RED)
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
