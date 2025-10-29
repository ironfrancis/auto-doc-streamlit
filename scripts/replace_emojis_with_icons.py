#!/usr/bin/env python3
"""
批量替换页面中的 emoji 为 SVG 图标
"""

import os
import re
from pathlib import Path

# Emoji 到图标的映射
EMOJI_TO_ICON_MAP = {
    "✅": "check",
    "❌": "x",
    "⚠️": "warning",
    "🔧": "wrench",
    "🧪": "flask",
    "📋": "clipboard",
    "➕": "plus",
    "✏️": "pencil",
    "👁️": "eye",
    "▶️": "play",
    "🗑️": "trash",
    "📊": "chart-bar",
    "📅": "calendar-blank",
    "🕐": "clock",
    "📥": "download",
    "🔍": "magnifying-glass",
    "🚀": "rocket",
    "🎨": "paint-brush-broad",
    "🔑": "key",
    "📂": "folder",
    "📝": "note-pencil",
    "📸": "camera",
    "⬇️": "download",
    "💾": "floppy-disk",
    "💡": "lightbulb",
    "🔄": "arrow-clockwise",
    "🖼️": "image-square",
    "📡": "list",
}


def replace_emojis_in_file(file_path: Path) -> tuple[int, bool]:
    """
    替换文件中的 emoji
    
    Returns:
        (替换次数, 是否修改过文件)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements = 0
        
        # 检查是否已经导入了 icon_library
        has_icon_import = 'from core.utils.icon_library import get_icon' in content
        
        # 替换每个 emoji
        for emoji, icon_name in EMOJI_TO_ICON_MAP.items():
            # 匹配各种 emoji 使用场景
            patterns = [
                # st.button("🚀 文本")
                (rf'st\.button\(\s*["\']({re.escape(emoji)})\s+([^"\']+)["\']\s*,', 
                 lambda m: f'st.button(f"{{get_icon(\'{icon_name}\')}} {m.group(2)}", unsafe_allow_html=True,'),
                
                # st.tabs(["🔧 文本", ...])
                (rf'["\']{re.escape(emoji)}\s+([^"\']+)["\']',
                 lambda m: f'f"{{get_icon(\'{icon_name}\')}} {m.group(1)}"'),
                
                # st.title("🔍 文本")
                (rf'st\.(title|header|subheader|markdown)\(\s*["\']({re.escape(emoji)})\s+([^"\']+)["\']\s*\)',
                 lambda m: f'st.{m.group(1)}(f"{{get_icon(\'{icon_name}\')}} {m.group(3)}", unsafe_allow_html=True)'),
                
                # "✅ 文本" 在f-string或普通字符串中 - 只在非f-string中替换
                (rf'(?<!f)(["\'])({re.escape(emoji)})\s+',
                 lambda m: f'f{m.group(1)}{{get_icon(\'{icon_name}\')}} '),
            ]
            
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    replacements += (new_content.count(icon_name) - content.count(icon_name))
                    content = new_content
        
        # 如果有替换并且还没有导入，添加导入语句
        if replacements > 0 and not has_icon_import:
            # 在其他导入之后添加
            import_pattern = r'(from core\.utils\.theme_loader import [^\n]+\n)'
            if re.search(import_pattern, content):
                content = re.sub(
                    import_pattern,
                    r'\1from core.utils.icon_library import get_icon\n',
                    content
                )
            else:
                # 如果没有 theme_loader，在第一个 import streamlit 之后添加
                import_pattern = r'(import streamlit as st\n)'
                content = re.sub(
                    import_pattern,
                    r'\1from core.utils.icon_library import get_icon\n',
                    content
                )
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return replacements, True
        
        return 0, False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, False


def main():
    """主函数"""
    pages_dir = Path(__file__).parent.parent / "pages"
    
    print("开始替换 pages 目录中的 emoji...\n")
    
    total_files = 0
    total_replacements = 0
    modified_files = []
    
    # 处理所有 Python 文件
    for file_path in pages_dir.glob("*.py"):
        # 跳过 backup 目录
        if "backup" in str(file_path):
            continue
        
        replacements, modified = replace_emojis_in_file(file_path)
        total_files += 1
        
        if modified:
            total_replacements += replacements
            modified_files.append(file_path.name)
            print(f"✓ {file_path.name}: {replacements} 处替换")
        else:
            print(f"  {file_path.name}: 无需替换")
    
    print(f"\n完成！")
    print(f"- 检查文件数: {total_files}")
    print(f"- 修改文件数: {len(modified_files)}")
    print(f"- 总替换次数: {total_replacements}")
    
    if modified_files:
        print(f"\n修改的文件:")
        for filename in modified_files:
            print(f"  - {filename}")


if __name__ == "__main__":
    main()

