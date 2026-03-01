#!/usr/bin/env python3
"""
统一博客处理脚本
整合转换、上传、生成博文三个步骤
根据 conversion_record.json 跳过已处理的文件夹
"""

import os
import json
import subprocess
import sys
from pathlib import Path

# 路径配置
IMAGE_PATH = r"C:\huang\Image"
IMAGE_1_PATH = r"C:\huang\Image-1"
ASTRO_POSTS_PATH = r"C:\huang\astro-melody-starter\src\content\posts"
CONVERSION_RECORD_PATH = os.path.join(IMAGE_PATH, "conversion_record.json")

def load_conversion_record():
    """加载转换记录"""
    if os.path.exists(CONVERSION_RECORD_PATH):
        try:
            with open(CONVERSION_RECORD_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] 无法读取转换记录: {str(e)}")
            return {}
    return {}

def save_conversion_record(record):
    """保存转换记录"""
    try:
        with open(CONVERSION_RECORD_PATH, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        print(f"[OK] 转换记录已保存到: {CONVERSION_RECORD_PATH}")
    except Exception as e:
        print(f"[ERROR] 无法保存转换记录: {str(e)}")

def get_unprocessed_folders():
    """获取未处理的文件夹列表"""
    record = load_conversion_record()
    unprocessed = []
    
    for folder in os.listdir(IMAGE_PATH):
        folder_path = os.path.join(IMAGE_PATH, folder)
        # 跳过文件和特殊目录
        if not os.path.isdir(folder_path):
            continue
        if folder in ['conversion_record.json', 'convert_to_webp.py', 'convert_to_webp_size_optimized.py', 'convert_to_webp.bat']:
            continue
        
        # 检查是否已处理
        if folder_path in record:
            print(f"[SKIP] 已处理过的文件夹: {folder}")
        else:
            unprocessed.append(folder)
    
    return unprocessed, record

def step1_convert(folder_name):
    """步骤1: 转换图片为WebP格式"""
    print(f"\n{'='*60}")
    print(f"步骤1: 转换图片 - {folder_name}")
    print(f"{'='*60}")
    
    # 执行转换脚本
    result = subprocess.run(
        [sys.executable, "convert_to_webp_size_optimized.py"],
        cwd=IMAGE_PATH,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"[OK] 转换完成: {folder_name}")
        return True
    else:
        print(f"[ERROR] 转换失败: {folder_name}")
        print(result.stderr)
        return False

def step2_upload(folder_name):
    """步骤2: 上传到R2存储"""
    print(f"\n{'='*60}")
    print(f"步骤2: 上传到R2 - {folder_name}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        [sys.executable, "upload_to_r2.py"],
        cwd=IMAGE_1_PATH,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"[OK] 上传完成: {folder_name}")
        return True
    else:
        print(f"[ERROR] 上传失败: {folder_name}")
        print(result.stderr)
        return False

def step3_generate_markdown(folder_name):
    """步骤3: 生成博文Markdown文件"""
    print(f"\n{'='*60}")
    print(f"步骤3: 生成博文 - {folder_name}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        [sys.executable, "generate_markdown.py"],
        cwd=IMAGE_1_PATH,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"[OK] 博文生成完成: {folder_name}")
        return True
    else:
        print(f"[ERROR] 博文生成失败: {folder_name}")
        print(result.stderr)
        return False

def add_to_record(record, folder_name):
    """将文件夹添加到处理记录"""
    folder_path = os.path.join(IMAGE_PATH, folder_name)
    target_path = os.path.join(IMAGE_1_PATH, folder_name)
    
    # 统计处理的文件数
    file_count = 0
    if os.path.exists(target_path):
        for f in os.listdir(target_path):
            if f.lower().endswith('.webp'):
                file_count += 1
    
    record[folder_path] = {
        "converted_count": file_count,
        "target_directory": target_path,
        "timestamp": os.path.getmtime(folder_path) if os.path.exists(folder_path) else None
    }
    
    return record

def main():
    print("="*60)
    print("博客处理流程")
    print("="*60)
    print()
    
    # 获取未处理的文件夹
    unprocessed_folders, record = get_unprocessed_folders()
    
    if not unprocessed_folders:
        print("\n[INFO] 没有新的文件夹需要处理")
        print("[INFO] 所有文件夹都已处理完成")
        return
    
    print(f"\n发现 {len(unprocessed_folders)} 个新文件夹需要处理:")
    for folder in unprocessed_folders:
        print(f"  - {folder}")
    print()
    
    # 处理每个新文件夹
    success_count = 0
    failed_folders = []
    
    for folder_name in unprocessed_folders:
        print(f"\n{'#'*60}")
        print(f"# 开始处理: {folder_name}")
        print(f"{'#'*60}")
        
        # 执行三个步骤
        step1_success = step1_convert(folder_name)
        if not step1_success:
            failed_folders.append((folder_name, "转换失败"))
            continue
        
        step2_success = step2_upload(folder_name)
        if not step2_success:
            failed_folders.append((folder_name, "上传失败"))
            continue
        
        step3_success = step3_generate_markdown(folder_name)
        if not step3_success:
            failed_folders.append((folder_name, "生成博文失败"))
            continue
        
        # 添加到记录
        record = add_to_record(record, folder_name)
        save_conversion_record(record)
        
        success_count += 1
        print(f"\n[OK] 成功处理: {folder_name}")
    
    # 总结
    print("\n" + "="*60)
    print("处理完成总结")
    print("="*60)
    print(f"成功处理: {success_count} 个文件夹")
    print(f"处理失败: {len(failed_folders)} 个文件夹")
    
    if failed_folders:
        print("\n失败的文件夹:")
        for folder, reason in failed_folders:
            print(f"  - {folder}: {reason}")
    
    print(f"\n总共已处理: {len(record)} 个文件夹")
    print("="*60)

if __name__ == "__main__":
    main()
