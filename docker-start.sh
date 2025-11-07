#!/bin/bash
# Docker 启动脚本 - 多服务架构
# 使用方法: ./docker-start.sh [选项]
#
# 选项:
#   --build, -b     构建 Docker 镜像
#   --dev, -d       开发模式（启用热重载）
#   --detach, -D    后台启动
#   --migrate       运行数据迁移

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🐳 准备启动 Docker 容器（多服务架构）..."

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

# 检查是否需要构建
if [ "$1" == "--build" ] || [ "$1" == "-b" ]; then
    echo "🔨 构建 Docker 镜像..."
    $COMPOSE_CMD build
    shift
fi

# 检查是否需要迁移数据
if [ "$1" == "--migrate" ]; then
    echo "📦 运行数据迁移..."
    $COMPOSE_CMD up -d postgres
    echo "⏳ 等待数据库就绪..."
    sleep 5
    $COMPOSE_CMD exec -T fastapi python scripts/migrate_json_to_db.py || echo "⚠️  迁移脚本需要在容器运行后执行"
    shift
fi

# 检查服务健康状态
check_health() {
    echo "🔍 检查服务健康状态..."
    
    # 检查 PostgreSQL
    if $COMPOSE_CMD ps postgres | grep -q "Up"; then
        echo "✅ PostgreSQL 运行中"
    else
        echo "⚠️  PostgreSQL 未运行"
    fi
    
    # 检查 FastAPI
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ FastAPI 运行中"
    else
        echo "⚠️  FastAPI 未响应"
    fi
    
    # 检查 Streamlit
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "✅ Streamlit 运行中"
    else
        echo "⚠️  Streamlit 未响应"
    fi
}

# 检查是否使用开发模式
if [ "$1" == "--dev" ] || [ "$1" == "-d" ]; then
    echo "🔧 启动开发模式..."
    $COMPOSE_CMD -f docker-compose.yml -f docker-compose.dev.yml up
elif [ "$1" == "--detach" ] || [ "$1" == "-D" ]; then
    echo "🚀 后台启动容器..."
    $COMPOSE_CMD up -d
    
    echo ""
    echo "⏳ 等待服务启动..."
    sleep 10
    
    check_health
    
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
    echo "   - 查看所有服务:   $COMPOSE_CMD ps"
    echo "   - 停止服务:       $COMPOSE_CMD down"
    echo "   - 数据迁移:       $COMPOSE_CMD exec fastapi python scripts/migrate_json_to_db.py"
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

