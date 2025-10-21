#!/bin/bash
# Auto-doc-streamlit 快速启动脚本
# 使用方法: ./start_project.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 启动 Auto-doc-streamlit 项目..."

# 激活虚拟环境
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 虚拟环境不存在，请先运行: uv sync"
    exit 1
fi

# 切换到项目目录
cd "$PROJECT_DIR"

# 检查依赖
echo "🔍 检查依赖..."
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit 未安装，正在安装依赖..."
    uv sync
fi

# 启动应用
echo "🎯 启动 Streamlit 应用..."
echo "📱 应用将在浏览器中打开: http://localhost:8501"
echo "💡 按 Ctrl+C 停止应用"
echo ""

streamlit run homepage.py
