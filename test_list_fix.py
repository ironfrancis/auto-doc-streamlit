#!/usr/bin/env python3
"""
测试Markdown列表转换的修复
"""

import sys
import os
sys.path.append('/Users/xuchao/Projects/备份项目/Auto-doc-streamlit')

from core.utils.md_utils import md_to_html

# 测试Markdown内容
test_md = """
# 测试列表

这是一个无序列表：

- 项目1
- 项目2
- 项目3

这是一个有序列表：

1. 第一项
2. 第二项
3. 第三项

嵌套列表：

- 主要项目1
  - 子项目1.1
  - 子项目1.2
- 主要项目2
  - 子项目2.1
"""

if __name__ == "__main__":
    print("测试Markdown列表转换...")

    # 生成HTML
    html_result = md_to_html(test_md, template_name='06_agi-observation-room-article-template.html')

    # 保存到文件
    output_file = "/Users/xuchao/Projects/备份项目/Auto-doc-streamlit/test_list_output.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_result)

    print(f"测试结果已保存到: {output_file}")

    # 检查HTML中是否包含正确的样式
    if 'margin-bottom: 6px' in html_result:
        print("✅ 修复成功：list-item 样式已更新为 margin-bottom: 6px")
    else:
        print("❌ 修复失败：未找到预期的样式")

    # 检查是否还有错误的样式
    if 'margin-bottom: 12px' in html_result:
        print("⚠️  警告：仍存在旧的 margin-bottom: 12px 样式")
    else:
        print("✅ 确认：不再存在旧的 margin-bottom: 12px 样式")
