import os
from pathlib import Path
from datetime import datetime
import json

# Configuration
IMAGE_1_PATH = r"C:\huang\Image-1"
ASTRO_POSTS_PATH = r"C:\huang\astro-melody-starter\src\content\posts"
R2_BASE_URL = "https://pub-58906530c3a643c1b5d1101b21b03114.r2.dev"

# Excluded files and directories
EXCLUDED_NAMES = {'conversion_record.json', 'upload_to_r2.ps1', 'upload_to_r2.py', 'convert_to_webp.py', 'convert_to_webp.bat', 'README_upload_script.md', 'ceshi.txt', 'files.txt'}

def get_webp_files(folder_path):
    """Get all webp files in a folder"""
    webp_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.webp'):
            webp_files.append(file)
    return sorted(webp_files)

def generate_markdown(folder_name, webp_files):
    """Generate markdown content for a folder"""
    # Convert folder name to slug (replace spaces with hyphens, keep original case)
    slug = folder_name.replace(' ', '-')
    
    # Use first image as cover
    cover_url = f"{R2_BASE_URL}/{slug}/{webp_files[0]}"
    
    # Generate frontmatter
    frontmatter = f"""---
author: Image Gallery
category:
- Gallery
cover: {cover_url}
coverAlt: {folder_name} gallery image
description: A collection of images from {folder_name}
pubDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
slug: {slug}
tags:
- images
- gallery
title: {folder_name}
---

"""
    
    # Generate image gallery content
    content = f"# {folder_name}\n\n"
    content += f"This gallery contains {len(webp_files)} images.\n\n"
    content += "## Image Gallery\n\n"
    
    for img_file in webp_files:
        img_url = f"{R2_BASE_URL}/{slug}/{img_file}"
        content += f"![{img_file}]({img_url})\n\n"
    
    return frontmatter + content

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
        
        # Generate filename
        slug = folder_name.replace(' ', '-').lower()
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
