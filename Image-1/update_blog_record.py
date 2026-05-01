import os
import re
from pathlib import Path
from datetime import datetime

POSTS_DIR = r"C:\huang\astro-melody-starter\src\content\posts"
RECORD_FILE = r"C:\huang\博文发布记录.md"

def extract_post_info(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        if not title_match:
            return None
        title = title_match.group(1).strip()
        pubdate_match = re.search(r'^pubDate:\s*(.+?)$', content, re.MULTILINE)
        if not pubdate_match:
            return None
        pubdate_str = pubdate_match.group(1).strip()
        for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d']:
            try:
                pubdate = datetime.strptime(pubdate_str[:19], fmt[:19])
                return {'title': title, 'date': pubdate.strftime('%Y-%m-%d'), 'file': file_path}
            except ValueError:
                continue
        return None
    except Exception:
        return None

def read_all_recorded_titles():
    if not os.path.exists(RECORD_FILE):
        return set()
    with open(RECORD_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    titles = set()
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('- ') and not line.startswith('- ##') and not line.startswith('- #'):
            title = line[2:].strip()
            if title and not re.match(r'^\d{2}-\d{2}$', title):
                titles.add(title)
    return titles

def main():
    print("扫描博文目录...")
    post_files = list(Path(POSTS_DIR).glob('*.md'))
    print(f"找到 {len(post_files)} 个博文文件")

    print("提取博文信息...")
    all_posts = []
    for fp in post_files:
        info = extract_post_info(fp)
        if info:
            all_posts.append(info)

    print("读取已有发布记录...")
    recorded_titles = read_all_recorded_titles()
    print(f"已记录 {len(recorded_titles)} 篇博文")

    new_posts = [p for p in all_posts if p['title'] not in recorded_titles]
    print(f"发现 {len(new_posts)} 篇新博文需要添加")

    if not new_posts:
        print("没有新博文需要添加，无需更新。")
        return

    new_by_date = {}
    for p in new_posts:
        d = p['date']
        if d not in new_by_date:
            new_by_date[d] = []
        new_by_date[d].append(p['title'])

    with open(RECORD_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    header_end = content.find('\n## ')
    if header_end == -1:
        header_end = len(content)

    header = content[:header_end]
    old_body = content[header_end:]

    new_sections = ""
    for date_str in sorted(new_by_date.keys(), reverse=True):
        posts = new_by_date[date_str]
        new_sections += f"\n## {date_str}\n\n### 图片博文\n- {date_str[-5:]}\n"
        for title in posts:
            new_sections += f"- {title}\n\n"

    updated = header + new_sections + old_body

    with open(RECORD_FILE, 'w', encoding='utf-8') as f:
        f.write(updated)

    print(f"\n✅ 已添加 {len(new_posts)} 篇新博文到发布记录:")
    for date_str in sorted(new_by_date.keys(), reverse=True):
        for title in new_by_date[date_str]:
            print(f"  [{date_str}] {title}")

if __name__ == "__main__":
    main()
