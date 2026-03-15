import re

frontmatter = '''category:
  - R18
cover: h
ttps://image.91tutu.cc/image/%E7%88%B1%E8%8E%89%20-%20No.004%20Nikke%20White%20Rabbit%20%5B17P-160MB%5D/001.webp
coverAlt: "爱莉 - No.004 Nikke White Rabbit [17P-160MB]"
description: "爱莉 - No.004 Nikke White Rabbit [17P-160MB] - 17张高清写真图片"
pubDate: 2026-03-12
23: 1
7: 0
0:33
slug: aili-No004-Nikke-White-Rabbit-17P-160MB'''

# 测试替换
result = re.sub(r'cover:\s*h\s*ttps?:\s*//', 'cover: https://', frontmatter)
print('After cover replacement:')
print(result[:300])

# 检查
if 'https://' in result:
    print('\nSUCCESS: URL was fixed')
else:
    print('\nFAILED: URL was not fixed')
