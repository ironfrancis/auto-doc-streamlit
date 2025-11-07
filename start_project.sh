#!/bin/bash
# Auto-doc-streamlit Docker 启动脚本
# 使用方法: ./start_project.sh [选项]
#
# 选项:
#   --build, -b     重新构建镜像
#   --detach, -d    后台运行
#   --dev           开发模式（热重载）

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🐳 Auto-doc-streamlit Docker 启动脚本"
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查 docker-compose 是否可用
if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
    echo "❌ docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

# 确定使用的命令
if docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "✅ 使用命令: $COMPOSE_CMD"
echo ""

# 检查是否需要构建
if [ "$1" == "--build" ] || [ "$1" == "-b" ]; then
    echo "🔨 构建 Docker 镜像..."
    $COMPOSE_CMD build
    shift
fi

# 检查是否使用开发模式
if [ "$1" == "--dev" ]; then
    echo "🔧 启动开发模式（热重载）..."
    $COMPOSE_CMD -f docker-compose.yml -f docker-compose.dev.yml up
elif [ "$1" == "--detach" ] || [ "$1" == "-d" ]; then
    echo "🚀 后台启动容器..."
    $COMPOSE_CMD up -d
    
    echo ""
    echo "⏳ 等待服务启动..."
    sleep 5
    
    echo ""
    echo "✅ 容器已在后台启动"
    echo ""
    echo "📱 服务访问地址:"
    echo "   - Streamlit 前端: http://localhost:8501"
    echo "   - FastAPI 后端:   http://localhost:8000"
    echo "   - API 文档:       http://localhost:8000/docs"
    echo ""
    echo "📋 常用命令:"
    echo "   - 查看日志:       $COMPOSE_CMD logs -f"
    echo "   - 查看状态:       $COMPOSE_CMD ps"
    echo "   - 停止服务:       $COMPOSE_CMD down"
else
    echo "🚀 启动容器..."
    echo ""
    echo "📱 服务访问地址:"
    echo "   - Streamlit 前端: http://localhost:8501"
    echo "   - FastAPI 后端:   http://localhost:8000"
    echo "   - API 文档:       http://localhost:8000/docs"
    echo ""
    echo "💡 按 Ctrl+C 停止应用"
    echo ""
    $COMPOSE_CMD up
fi
