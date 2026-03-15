import os
import re

filepath = r"c:\huang\astro-melody-starter\src\content\posts\aili-No005-xilian-19P-140MB.md"

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print("\nFirst 10 lines:")
for i, line in enumerate(lines[:10]):
    print(f"Line {i}: {repr(line)}")
