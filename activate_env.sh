#!/bin/bash
# Auto-doc-streamlit 项目环境激活脚本
# 使用方法: source activate_env.sh

# 获取脚本所在目录（项目根目录）
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo "🚀 正在激活 Auto-doc-streamlit 项目环境..."
echo "📁 项目目录: $PROJECT_DIR"

# 检查虚拟环境是否存在
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ 虚拟环境不存在: $VENV_DIR"
    echo "💡 请先运行: uv sync"
    return 1
fi

# 检查激活脚本是否存在
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "❌ 虚拟环境激活脚本不存在: $VENV_DIR/bin/activate"
    return 1
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 切换到项目目录
cd "$PROJECT_DIR"

# 显示环境信息
echo "✅ 虚拟环境已激活"
echo "🐍 Python 版本: $(python --version)"
echo "📦 包管理器: $(which uv)"
echo "📁 当前目录: $(pwd)"

# 检查关键依赖
echo ""
echo "🔍 检查关键依赖:"
if command -v streamlit &> /dev/null; then
    echo "  ✅ Streamlit: $(streamlit --version)"
else
    echo "  ❌ Streamlit 未安装"
fi

if command -v uv &> /dev/null; then
    echo "  ✅ uv: $(uv --version)"
else
    echo "  ❌ uv 未安装"
fi

echo ""
echo "🎯 快速启动命令:"
echo "  streamlit run homepage.py    # 启动主应用"
echo "  uv sync                      # 同步依赖"
echo "  uv add <package>             # 添加新包"
echo ""
echo "💡 提示: 使用 'deactivate' 退出虚拟环境"


# # 基础静默模式（无浏览器、无头模式、仅输出错误日志）
# nohup streamlit run /www/wwwroot/auto-doc-streamlit/homepage.py \
#   --server.headless=true \          # 无头模式（无GUI窗口，必选）
#   --server.browser.serverAddress=0.0.0.0 \  # 允许外部访问（可选，默认127.0.0.1）
#   --server.port=8501 \              # 指定端口（可选，默认8501）
#   --logger.level=ERROR \            # 仅输出错误日志（禁用INFO/WARNING，可选）
#   --server.fileWatcherType=none \   # 禁用文件热重载（可选，生产级静默）
#   --server.enableDevMode=false \    # 禁用开发模式（可选，关闭调试特性）
#   > /dev/null 2>&1 &                # 重定向日志到黑洞（彻底静默，可选）