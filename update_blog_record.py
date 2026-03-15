import os
import re
from pathlib import Path
from datetime import datetime

# 配置
POSTS_DIR = r"C:\huang\astro-melody-starter\src\content\posts"
RECORD_FILE = r"C:\huang\博文发布记录.md"

# 读取markdown文件的标题和发布日期
def extract_post_info(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题
        title_match = re.search(r'title:\s*(.+?)(?:\n|$)', content)
        if not title_match:
            return None
        title = title_match.group(1).strip()
        # 去除引号
        if (title.startswith('"') and title.endswith('"')) or (title.startswith('\'') and title.endswith('\'')):
            title = title[1:-1]
        
        # 提取发布日期
        pubdate_match = re.search(r'pubDate:\s*(.+?)(?:\n|$)', content)
        if not pubdate_match:
            return None
        pubdate_str = pubdate_match.group(1).strip()
        
        # 解析日期
        try:
            # 尝试多种日期格式
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d']:
                try:
                    pubdate = datetime.strptime(pubdate_str, fmt)
                    return {'title': title, 'date': pubdate.strftime('%Y-%m-%d'), 'file': file_path}
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    except Exception:
        return None

# 读取现有发布记录
def read_existing_records():
    records = {}
    if not os.path.exists(RECORD_FILE):
        return records
    
    with open(RECORD_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有日期和对应的标题
    date_sections = re.findall(r'##\s*(\d{4}-\d{2}-\d{2})[\s\S]*?(?=##|$)', content)
    for date_str in date_sections:
        section_match = re.search(r'##\s*' + re.escape(date_str) + r'[\s\S]*?(?=##|$)', content)
        if section_match:
            section = section_match.group(0)
            # 提取图片博文标题
            posts = re.findall(r'-\s*(.+?)(?:\n|$)', section)
            records[date_str] = [p.strip() for p in posts if p.strip()]
    
    return records

# 生成更新后的发布记录
def generate_updated_record(existing_records, new_posts):
    # 合并现有记录和新记录
    all_records = {**existing_records}
    for date_str, posts in new_posts.items():
        if date_str not in all_records:
            all_records[date_str] = []
        # 添加新帖子，避免重复
        for post in posts:
            if post not in all_records[date_str]:
                all_records[date_str].append(post)
    
    # 按日期排序
    sorted_dates = sorted(all_records.keys(), reverse=True)
    
    # 生成Markdown内容
    content = "# 博文发布记录\n\n本文件记录每次发布的博文标题，便于追踪和管理。\n\n"
    
    for date_str in sorted_dates:
        posts = all_records[date_str]
        if not posts:
            continue
        
        content += f"## {date_str}\n\n"
        content += "### 图片博文\n"
        for post in posts:
            content += f"- {post}\n"
        content += "\n"
    
    return content

def main():
    print("开始扫描博文文件...")
    
    # 扫描所有markdown文件
    post_files = list(Path(POSTS_DIR).glob('*.md'))
    print(f"找到 {len(post_files)} 个博文文件")
    
    # 提取所有帖子信息
    posts_by_date = {}
    for file_path in post_files:
        info = extract_post_info(file_path)
        if info:
            date_str = info['date']
            if date_str not in posts_by_date:
                posts_by_date[date_str] = []
            posts_by_date[date_str].append(info['title'])
    
    print("读取现有发布记录...")
    existing_records = read_existing_records()
    
    print("生成更新后的发布记录...")
    updated_content = generate_updated_record(existing_records, posts_by_date)
    
    # 写入文件
    with open(RECORD_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"发布记录已更新到 {RECORD_FILE}")
    
    # 统计信息
    total_posts = sum(len(posts) for posts in posts_by_date.values())
    print(f"总计 {total_posts} 篇博文")

if __name__ == "__main__":
    main()
