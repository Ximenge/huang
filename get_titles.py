import os
import re
from datetime import datetime
from pathlib import Path

def extract_titles_from_recent_files():
    # 切换到目标目录
    target_dir = Path('./astro-melody-starter/src/content/posts')
    os.chdir(target_dir)
    
    today = datetime.now()
    titles = []

    for file in Path('.').glob('*.md'):
        mod_time = datetime.fromtimestamp(file.stat().st_mtime)
        if (today - mod_time).days <= 1:  # 文件在过去一天内被修改
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找title行
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('title:'):
                        title_part = line[6:].strip()  # 去掉 'title:' 部分
                        # 去除前后引号
                        title_part = title_part.strip().strip('"\'')
                        titles.append(title_part)
                        break
            except Exception as e:
                print(f'Error reading {file}: {e}')

    # 输出排序后的标题列表
    for title in sorted(titles):
        print(f'- {title}')
    
    print(f'\nTotal: {len(titles)} files')

if __name__ == '__main__':
    extract_titles_from_recent_files()