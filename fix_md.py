import os
import re

posts_dir = r"c:\huang\astro-melody-starter\src\content\posts"
fixed_count = 0

for filename in os.listdir(posts_dir):
    if not filename.endswith('.md'):
        continue
    
    filepath = os.path.join(posts_dir, filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    modified = False
    seen_pubDate = False
    
    while i < len(lines):
        line = lines[i]
        
        # Fix 1: "https:: //" -> "https://" (double colon)
        if 'https:: //' in line:
            line = line.replace('https:: //', 'https://')
            modified = True
        
        # Fix 2: "https: //" -> "https://" (space after colon)
        if 'https: //' in line:
            line = line.replace('https: //', 'https://')
            modified = True
        
        # Fix 3: cover broken as "cover: http" + "s: //..." -> "cover: https://..."
        if line.strip() == 'cover: http' and i + 1 < len(lines):
            next_line = lines[i+1].strip()
            if next_line.startswith('s:'):
                rest = next_line[1:].strip()  # Remove "s:" and get "//..."
                new_lines.append('cover: https:' + rest + '\n')
                i += 2
                modified = True
                continue
        
        # Fix 4: pubDate with time -> just date
        if re.match(r'pubDate: \d{4}-\d{2}-\d{2} \d+:\d+:\d+', line):
            line = re.sub(r'(pubDate: \d{4}-\d{2}-\d{2}) \d+:\d+:\d+', r'\1', line)
            modified = True
        
        # Fix 5: Remove duplicate pubDate lines (keep first one)
        if line.startswith('pubDate:'):
            if seen_pubDate:
                # Skip this duplicate pubDate line
                i += 1
                modified = True
                continue
            else:
                seen_pubDate = True
        
        # Fix 6: double quotes "" -> "
        if '""' in line:
            line = line.replace('""', '"')
            modified = True
        
        new_lines.append(line)
        i += 1
    
    # Fix 7: Add --- after title if missing
    final_lines = []
    i = 0
    while i < len(new_lines):
        line = new_lines[i]
        final_lines.append(line)
        
        # Check if this is a title line
        if line.startswith('title:'):
            # Check if next line is ---
            if i + 1 < len(new_lines) and new_lines[i+1].strip() != '---':
                # Add --- after title
                final_lines.append('---\n')
                modified = True
        i += 1
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(final_lines)
        fixed_count += 1
        print(f"Fixed: {filename}")

print(f"\nTotal fixed: {fixed_count} files")
