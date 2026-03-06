import os
from pathlib import Path
from datetime import datetime
import json
from urllib.parse import quote
import re
from pypinyin import lazy_pinyin

# Configuration
IMAGE_ORIGINAL_PATH = r"C:\huang\image"
IMAGE_1_PATH = r"C:\huang\Image-1"
ASTRO_POSTS_PATH = r"C:\huang\astro-melody-starter\src\content\posts"
R2_BASE_URL = "https://image.91tutu.cc"

# Excluded files and directories
EXCLUDED_NAMES = {'conversion_record.json', 'upload_to_r2.ps1', 'upload_to_r2.py', 'convert_to_webp.py', 'convert_to_webp.bat', 'README_upload_script.md', 'ceshi.txt', 'files.txt'}

def get_webp_files(folder_path):
    """Get all webp files in a folder"""
    webp_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.webp'):
            webp_files.append(file)
    return sorted(webp_files)

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

def load_metadata(folder_name):
    """Load metadata from post_metadata.json if exists (from original image folder)"""
    metadata_path = os.path.join(IMAGE_ORIGINAL_PATH, folder_name, 'post_metadata.json')
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"  [WARNING] Failed to read metadata: {str(e)}")
    return None

def generate_markdown(folder_name, webp_files):
    """Generate markdown content for a folder"""
    # Sanitize slug for Cloudflare Pages compatibility
    slug = sanitize_slug(folder_name)
    # URL encode the original folder name for R2 URLs
    slug_encoded = quote(folder_name, safe='')
    
    # Load metadata
    metadata = load_metadata(folder_name)
    
    # Default values
    category = "Gallery"
    tags = ["images", "gallery"]
    description = ""
    
    if metadata:
        category = metadata.get("category", category)
        tags = metadata.get("tags", tags)
        description = metadata.get("description", "")
    
    # Use first image as cover
    cover_url = f"{R2_BASE_URL}/image/{slug_encoded}/{quote(webp_files[0], safe='')}"
    
    # 构建正文内容
    # 1. 添加图片（每张图片单独一行，使用 markdown 图片语法）
    body_content = ""
    for img_file in webp_files:
        img_url = f"{R2_BASE_URL}/image/{slug_encoded}/{quote(img_file, safe='')}"
        body_content += f"![{img_file}]({img_url})\n\n"
    
    # 2. 最后添加描述（如果有）
    if description:
        body_content += f"{description}\n\n"
    
    # 使用 yaml 库安全地生成 frontmatter
    frontmatter_data = {
        'category': [category],
        'cover': cover_url,
        'coverAlt': folder_name,
        'description': f"{folder_name} - {len(webp_files)}张图片",
        'pubDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'slug': slug,
        'tags': tags,
        'title': folder_name
    }
    
    # 手动构建 frontmatter，确保 pubDate 不被引号包裹
    frontmatter_lines = ["---"]
    
    # category
    frontmatter_lines.append("category:")
    for cat in frontmatter_data['category']:
        frontmatter_lines.append(f"- {escape_yaml_string(cat)}")
    
    # cover
    frontmatter_lines.append(f"cover: {frontmatter_data['cover']}")
    
    # coverAlt
    frontmatter_lines.append(f"coverAlt: {escape_yaml_string(frontmatter_data['coverAlt'])}")
    
    # description
    frontmatter_lines.append(f"description: {escape_yaml_string(frontmatter_data['description'])}")
    
    # pubDate - 不添加引号
    frontmatter_lines.append(f"pubDate: {frontmatter_data['pubDate']}")
    
    # slug
    frontmatter_lines.append(f"slug: {frontmatter_data['slug']}")
    
    # tags
    frontmatter_lines.append("tags:")
    for tag in frontmatter_data['tags']:
        frontmatter_lines.append(f"- {escape_yaml_string(tag)}")
    
    # title
    frontmatter_lines.append(f"title: {escape_yaml_string(frontmatter_data['title'])}")
    
    frontmatter_lines.append("---")
    frontmatter_lines.append("")
    frontmatter_lines.append("")
    
    frontmatter = "\n".join(frontmatter_lines)
    
    # 返回 frontmatter + 正文内容
    return frontmatter + body_content

def main():
    print("========================================")
    print("Markdown Generator for Astro Posts")
    print("========================================")
    print()
    
    # Get all subdirectories in Image-1
    image_1_path = Path(IMAGE_1_PATH)
    folders = [d for d in image_1_path.iterdir() if d.is_dir() and d.name not in EXCLUDED_NAMES]
    
    print(f"Found {len(folders)} folders to process:")
    for folder in folders:
        print(f"  - {folder.name}")
    print()
    
    # Process each folder
    generated_count = 0
    skipped_count = 0
    
    for folder in folders:
        folder_name = folder.name
        print(f"Processing folder: {folder_name}")
        
        # Get webp files
        webp_files = get_webp_files(folder)
        
        if not webp_files:
            print(f"  [SKIP] No webp files found in {folder_name}")
            skipped_count += 1
            continue
        
        print(f"  Found {len(webp_files)} webp files")
        
        # Generate markdown content
        markdown_content = generate_markdown(folder_name, webp_files)
        
        # Generate filename using sanitized slug
        slug = sanitize_slug(folder_name)
        md_filename = f"{slug}.md"
        md_path = os.path.join(ASTRO_POSTS_PATH, md_filename)
        
        # Check if file already exists
        if os.path.exists(md_path):
            print(f"  [SKIP] Markdown file already exists: {md_filename}")
            skipped_count += 1
            continue
        
        # Write markdown file
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"  [OK] Generated: {md_filename}")
            generated_count += 1
        except Exception as e:
            print(f"  [ERROR] Failed to write {md_filename}: {str(e)}")
        
        print()
    
    # Summary
    print("========================================")
    print("Generation Complete!")
    print("========================================")
    print(f"Successfully generated: {generated_count} markdown files")
    print(f"Skipped: {skipped_count} folders")
    print()

if __name__ == "__main__":
    main()
