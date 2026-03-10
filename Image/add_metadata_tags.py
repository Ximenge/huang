import os
import json
from pathlib import Path

def create_post_metadata_for_folders(base_path):
    """遍历指定路径下的所有文件夹，为没有post_metadata.json的文件夹创建该文件"""
    base_dir = Path(base_path)
    
    # 遍历所有子目录
    for folder in base_dir.iterdir():
        if folder.is_dir():
            print(f"正在检查文件夹: {folder.name}")
            
            # 检查是否已存在post_metadata.json
            metadata_file = folder / "post_metadata.json"
            
            if metadata_file.exists():
                print(f"  已存在post_metadata.json，跳过: {folder.name}")
            else:
                # 从文件夹名中提取标签（第一个空格前的部分）
                folder_name = folder.name
                first_space_index = folder_name.find(' ')
                
                if first_space_index != -1:
                    tag = folder_name[:first_space_index]
                else:
                    # 如果没有空格，则使用整个文件夹名作为标签
                    tag = folder_name
                
                # 创建metadata内容
                metadata_content = {
                    "category": "R18",
                    "tags": [tag]
                }
                
                # 写入文件
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata_content, f, ensure_ascii=False, indent=2)
                
                print(f"  创建post_metadata.json: {folder.name} (标签: {tag})")

# 指定基础路径
base_path = r"C:\huang\Image"

print("开始处理文件夹...")
create_post_metadata_for_folders(base_path)
print("处理完成！")