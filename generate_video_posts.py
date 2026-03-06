#!/usr/bin/env python3
"""
视频博文生成脚本 - 生成 .md 文件到 Content Collections
根据video-1文件夹结构生成视频博文

目录结构：
video-1/
├── 视频分组名称/        # 一级子目录 → 视频分组
│   └── 博文标题/        # 二级子目录 → 博文标题
│       ├── video/
│       │   └── playlist.m3u8
│       └── metadata.json

输出：
- src/content/videos/{分组}/{博文标题}.md
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
import re
from pypinyin import lazy_pinyin

# 配置
VIDEO_ORIGINAL_DIR = r"C:\huang\video"
VIDEO_OUTPUT_DIR = r"C:\huang\video-1"
CONTENT_VIDEOS_DIR = r"C:\huang\astro-melody-starter\src\content\videos"
GENERATION_RECORD_FILE = r"C:\huang\video_post_generation_record.json"
PUBLIC_VIDEOS_DIR = r"C:\huang\astro-melody-starter\public\videos-1"
R2_BASE_URL = "https://video.91tutu.cc"


def load_generation_record(json_path):
    """加载生成记录JSON文件"""
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告: 无法读取生成记录文件: {str(e)}")
            return {"generated_posts": {}}
    return {"generated_posts": {}}


def save_generation_record(json_path, record):
    """保存生成记录到JSON文件"""
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"警告: 无法保存生成记录文件: {str(e)}")


def is_post_generated(record, group_name, post_title):
    """检查博文是否已生成"""
    key = f"{group_name}/{post_title}"
    return key in record.get("generated_posts", {})


def add_post_record(record, group_name, post_title, video_count):
    """添加博文生成记录"""
    key = f"{group_name}/{post_title}"
    record["generated_posts"][key] = {
        "group_name": group_name,
        "post_title": post_title,
        "video_count": video_count
    }


def load_metadata(post_folder):
    """加载博文的metadata.json"""
    metadata_file = os.path.join(post_folder, "metadata.json")
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"      警告: 无法读取元数据文件: {str(e)}")
    return None

def sanitize_slug(name):
    """Convert Chinese to pinyin, replace spaces with hyphens, and create a clean slug"""
    # Convert Chinese characters to pinyin
    pinyin_list = lazy_pinyin(name)
    slug = ''.join(pinyin_list)
    
    # Replace spaces with hyphens
    slug = slug.replace(' ', '-')
    
    # Remove any characters that are not alphanumeric, hyphens, or underscores
    slug = re.sub(r'[^a-zA-Z0-9-_]', '', slug)
    
    # Replace multiple hyphens with single hyphen
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # If slug is empty (unlikely), use a default
    if not slug:
        slug = 'untitled'
    
    return slug

def escape_yaml_string(value):
    """转义 YAML 字符串，处理特殊字符"""
    if not isinstance(value, str):
        return str(value)
    
    # YAML 中需要引号包裹的特殊字符
    special_chars = [':', '{', '}', '[', ']', ',', '&', '*', '#', '?', '|', '-', '<', '>', '=', '!', '%', '@', '\\', '"', "'", '\n']
    
    if any(c in value for c in special_chars):
        # 双引号需要转义
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return value

def load_post_metadata(group_name, post_title):
    """从原始video目录加载post_metadata.json"""
    post_metadata_file = os.path.join(VIDEO_ORIGINAL_DIR, group_name, post_title, "post_metadata.json")
    if os.path.exists(post_metadata_file):
        try:
            with open(post_metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"      警告: 无法读取post_metadata.json: {str(e)}")
    
    # 尝试匹配转换后的目录名（将 --- 转换为 - ，将 - 转换为空格）
    # video-1 目录名格式: "紧急企划---奶昔---居家-[143P3V-8.50G]"
    # video 目录名格式: "紧急企划 - 奶昔 - 居家 [143P3V-8.50G]"
    converted_title = post_title.replace('---', ' - ').replace('-', ' ', 1)
    # 处理括号前的空格
    converted_title = converted_title.replace('-[', ' [')
    
    post_metadata_file = os.path.join(VIDEO_ORIGINAL_DIR, group_name, converted_title, "post_metadata.json")
    if os.path.exists(post_metadata_file):
        try:
            with open(post_metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"      警告: 无法读取post_metadata.json: {str(e)}")
    
    # 尝试遍历 video 目录下的分组目录，查找匹配的 post_metadata.json
    group_path = os.path.join(VIDEO_ORIGINAL_DIR, group_name)
    if os.path.exists(group_path):
        for folder_name in os.listdir(group_path):
            folder_path = os.path.join(group_path, folder_name)
            if os.path.isdir(folder_path):
                metadata_path = os.path.join(folder_path, "post_metadata.json")
                if os.path.exists(metadata_path):
                    # 检查文件夹名是否与 post_title 相似（忽略分隔符差异）
                    # 将两个名称都标准化后比较
                    normalized_folder = folder_name.replace(' ', '-').replace('---', '-')
                    normalized_title = post_title.replace(' ', '-').replace('---', '-')
                    # 移除特殊字符后比较
                    import re as re_module
                    clean_folder = re_module.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', normalized_folder)
                    clean_title = re_module.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', normalized_title)
                    if clean_folder == clean_title:
                        try:
                            with open(metadata_path, 'r', encoding='utf-8') as f:
                                return json.load(f)
                        except Exception as e:
                            print(f"      警告: 无法读取post_metadata.json: {str(e)}")
    
    return None


def generate_md_file(group_name, post_title, metadata, post_metadata=None):
    """生成 .md 文件"""
    # Sanitize group name and post title for directory and filename
    group_name_sanitized = sanitize_slug(group_name)
    post_title_sanitized = sanitize_slug(post_title)
    
    group_dir = os.path.join(CONTENT_VIDEOS_DIR, group_name_sanitized)
    os.makedirs(group_dir, exist_ok=True)
    
    md_file = os.path.join(group_dir, f"{post_title_sanitized}.md")
    
    videos = metadata.get("videos", [])
    video_count = len(videos)
    
    # URL encode group_name and post_title
    group_name_encoded = quote(group_name, safe='')
    post_title_encoded = quote(post_title, safe='')
    
    pub_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Default values
    category = "Video"
    tags = ["video", "vlog"]
    
    if post_metadata:
        category = post_metadata.get("category", category)
        tags = post_metadata.get("tags", tags)
    
    # 手动构建 frontmatter，确保格式正确
    frontmatter_lines = ["---"]
    frontmatter_lines.append(f"title: {escape_yaml_string(post_title)}")
    frontmatter_lines.append(f"series: {escape_yaml_string(group_name)}")
    frontmatter_lines.append(f"description: {escape_yaml_string(f'{post_title} - {video_count}个视频')}")
    frontmatter_lines.append(f"pubDate: {pub_date}")
    
    # 处理封面
    cover = metadata.get("cover")
    if cover:
        cover_url = f"{R2_BASE_URL}/video/{group_name_encoded}/{post_title_encoded}/{quote(cover, safe='')}"
        frontmatter_lines.append(f"cover: {cover_url}")
    
    # category
    frontmatter_lines.append("category:")
    frontmatter_lines.append(f"- {escape_yaml_string(category)}")
    
    # tags
    frontmatter_lines.append("tags:")
    for tag in tags:
        frontmatter_lines.append(f"- {escape_yaml_string(tag)}")
    
    # videoCount
    frontmatter_lines.append(f"videoCount: {video_count}")
    
    # videos
    frontmatter_lines.append("videos:")
    for video in videos:
        hls_path = video.get("hls_playlist", "")
        name = video.get("name", "")
        hls_path_encoded = quote(hls_path, safe='/')
        frontmatter_lines.append(f'  - name: {escape_yaml_string(name)}')
        frontmatter_lines.append(f"    hlsUrl: {R2_BASE_URL}/video/{group_name_encoded}/{post_title_encoded}/{hls_path_encoded}")
    
    frontmatter_lines.append("---")
    frontmatter_lines.append("")
    
    # 构建正文内容
    body_content = ""
    if post_metadata and post_metadata.get("description"):
        body_content += f"{post_metadata.get('description')}\n"
    body_content += "\n"
    
    content = "\n".join(frontmatter_lines) + body_content
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"      生成 .md 文件: {md_file}")
    return True





def process_video_posts():
    """处理视频博文生成"""
    print("=" * 60)
    print("视频博文生成脚本 - Content Collections")
    print("=" * 60)
    print(f"视频输出文件夹: {VIDEO_OUTPUT_DIR}")
    print(f"内容目录: {CONTENT_VIDEOS_DIR}")
    print("=" * 60)
    
    record = load_generation_record(GENERATION_RECORD_FILE)
    print(f"\n加载生成记录: {GENERATION_RECORD_FILE}")
    print(f"已记录的博文数: {len(record.get('generated_posts', {}))}")
    
    if not os.path.exists(VIDEO_OUTPUT_DIR):
        print(f"错误: 视频输出目录不存在: {VIDEO_OUTPUT_DIR}")
        return
    
    new_posts = 0
    
    for group_name in os.listdir(VIDEO_OUTPUT_DIR):
        group_path = os.path.join(VIDEO_OUTPUT_DIR, group_name)
        if not os.path.isdir(group_path):
            continue
        
        print(f"\n处理视频分组: {group_name}")
        
        for post_title in os.listdir(group_path):
            post_path = os.path.join(group_path, post_title)
            if not os.path.isdir(post_path):
                continue
            
            if is_post_generated(record, group_name, post_title):
                print(f"  跳过已生成: {post_title}")
                continue
            
            metadata = load_metadata(post_path)
            if not metadata:
                print(f"  跳过无元数据: {post_title}")
                continue
            
            post_metadata = load_post_metadata(group_name, post_title)
            
            videos = metadata.get("videos", [])
            video_count = len(videos)
            
            if generate_md_file(group_name, post_title, metadata, post_metadata):
                add_post_record(record, group_name, post_title, video_count)
                print(f"  添加博文: {post_title} ({video_count}个视频)")
                new_posts += 1
    
    if new_posts > 0:
        save_generation_record(GENERATION_RECORD_FILE, record)
    
    print("\n" + "=" * 60)
    print("处理完成!")
    print(f"新增博文: {new_posts}")
    print("=" * 60)


if __name__ == "__main__":
    process_video_posts()
