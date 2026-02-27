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

# 配置
VIDEO_OUTPUT_DIR = r"C:\huang\video-1"
CONTENT_VIDEOS_DIR = r"C:\huang\astro-melody-starter\src\content\videos"
GENERATION_RECORD_FILE = r"C:\huang\video_post_generation_record.json"
PUBLIC_VIDEOS_DIR = r"C:\huang\astro-melody-starter\public\videos-1"


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


def generate_md_file(group_name, post_title, metadata):
    """生成 .md 文件"""
    group_dir = os.path.join(CONTENT_VIDEOS_DIR, group_name)
    os.makedirs(group_dir, exist_ok=True)
    
    md_file = os.path.join(group_dir, f"{post_title}.md")
    
    videos = metadata.get("videos", [])
    video_count = len(videos)
    
    videos_yaml = []
    for video in videos:
        hls_path = video.get("hls_playlist", "")
        name = video.get("name", "")
        videos_yaml.append(f'  - name: "{name}"')
        videos_yaml.append(f'    hlsUrl: /videos-1/{group_name}/{post_title}/{hls_path}')
    
    pub_date = datetime.now().strftime("%Y-%m-%d")
    
    content = f'''---
title: {post_title}
series: {group_name}
description: {post_title} - {video_count}个视频
pubDate: "{pub_date}"
videoCount: {video_count}
videos:
{chr(10).join(videos_yaml)}
---
'''
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"      生成 .md 文件: {md_file}")
    return True


def copy_videos_to_public():
    """复制视频文件到public目录"""
    if os.path.exists(PUBLIC_VIDEOS_DIR):
        shutil.rmtree(PUBLIC_VIDEOS_DIR)
    
    if os.path.exists(VIDEO_OUTPUT_DIR):
        shutil.copytree(VIDEO_OUTPUT_DIR, PUBLIC_VIDEOS_DIR)
        print(f"  复制视频文件到: {PUBLIC_VIDEOS_DIR}")


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
            
            videos = metadata.get("videos", [])
            video_count = len(videos)
            
            if generate_md_file(group_name, post_title, metadata):
                add_post_record(record, group_name, post_title, video_count)
                print(f"  添加博文: {post_title} ({video_count}个视频)")
                new_posts += 1
    
    if new_posts > 0:
        save_generation_record(GENERATION_RECORD_FILE, record)
        
        print("\n" + "=" * 60)
        print("复制视频文件到public目录...")
        copy_videos_to_public()
    
    print("\n" + "=" * 60)
    print("处理完成!")
    print(f"新增博文: {new_posts}")
    print("=" * 60)


if __name__ == "__main__":
    process_video_posts()
