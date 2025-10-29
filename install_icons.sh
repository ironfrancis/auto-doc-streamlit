#!/bin/bash

# 图标库安装脚本
# 用于快速安装 streamlit-iconify 并测试图标版本首页

echo "🚀 开始安装图标库..."
echo ""

# 检查是否存在虚拟环境
if [ -d "venv" ]; then
    echo "✓ 检测到虚拟环境"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "✓ 检测到虚拟环境"
    source .venv/bin/activate
else
    echo "⚠️  未检测到虚拟环境，将在全局环境安装"
fi

echo ""
echo "📦 安装 streamlit-iconify..."
pip install streamlit-iconify

echo ""
echo "✅ 安装完成！"
echo ""
echo "现在你可以运行以下命令查看效果："
echo ""
echo "  1. 原版（emoji 图标）："
echo "     streamlit run homepage.py"
echo ""
echo "  2. 新版（Phosphor 图标）："
echo "     streamlit run homepage_with_icons.py"
echo ""
echo "💡 提示：推荐使用图标版本，更专业更美观！"
echo ""

