#!/bin/bash

# AI内容创作与分发平台 - 统一启动脚本

echo "🚀 AI内容创作与分发平台"
echo "================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import streamlit, plotly, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装依赖..."
    pip install streamlit plotly pandas
fi

# 启动主应用
echo "🌐 启动Streamlit应用..."
echo "📍 地址: http://localhost:8501"
echo "💡 提示: 按 Ctrl+C 停止应用"
echo "-" * 50

python3 start_app.py 