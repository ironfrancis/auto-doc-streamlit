#!/bin/bash
# Auto-doc-streamlit Docker 环境说明脚本
# 使用方法: source activate_env.sh
#
# 注意：本项目使用 Docker 部署，不需要本地虚拟环境
# 所有依赖都在 Docker 容器中管理

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🐳 Auto-doc-streamlit Docker 环境"
echo "📁 项目目录: $PROJECT_DIR"
echo ""

# 检查 Docker 是否可用
if command -v docker > /dev/null 2>&1; then
    echo "✅ Docker: $(docker --version)"
else
    echo "❌ Docker 未安装"
    echo "💡 请先安装 Docker: https://www.docker.com/get-started"
    return 1
fi

# 检查 docker-compose
if docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
    echo "✅ docker compose: $(docker compose version | head -1)"
elif command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
    echo "✅ docker-compose: $(docker-compose --version)"
else
    echo "❌ docker-compose 未安装"
    return 1
fi

echo ""
echo "🎯 快速启动命令:"
echo "  ./start_project.sh              # 启动所有服务"
echo "  ./start_project.sh --build     # 构建并启动"
echo "  ./start_project.sh --detach    # 后台启动"
echo "  ./start_project.sh --dev       # 开发模式（热重载）"
echo ""
echo "  $COMPOSE_CMD up -d             # 后台启动"
echo "  $COMPOSE_CMD logs -f           # 查看日志"
echo "  $COMPOSE_CMD ps                # 查看状态"
echo "  $COMPOSE_CMD down              # 停止服务"
echo ""
echo "📱 服务访问地址:"
echo "  - Streamlit 前端: http://localhost:8501"
echo "  - FastAPI 后端:   http://localhost:8000"
echo "  - API 文档:       http://localhost:8000/docs"
echo ""
echo "💡 提示:"
echo "  - 本项目使用 Docker 统一管理环境，无需本地虚拟环境"
echo "  - 所有 Python 依赖都在 Docker 容器中安装"
echo "  - 代码修改会自动热重载（开发模式）"
echo ""
