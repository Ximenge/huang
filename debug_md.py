import os
import re

filepath = r"c:\huang\astro-melody-starter\src\content\posts\aili-No005-xilian-19P-140MB.md"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Show first 500 chars
print("First 500 chars:")
print(repr(content[:500]))

# Check for patterns
print("\n--- Check patterns ---")
print(f"Contains 'https:\\n': {repr(chr(10)) in content}")
print(f"Contains 'https: //': {'https: //' in content}")
print(f"Contains 'https:\\\\n': {'https:\\n' in content}")

# Find cover line
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'cover:' in line.lower():
        print(f"\nLine {i}: {repr(line)}")
