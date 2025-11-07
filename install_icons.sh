#!/bin/bash
# 图标库安装脚本（Docker 环境）
# 本项目使用 Docker，依赖在容器中管理

echo "🚀 图标库安装说明"
echo ""
echo "本项目使用 Docker 部署，所有依赖都在容器中管理。"
echo ""
echo "📦 如果需要在容器中安装 streamlit-iconify，可以："
echo ""
echo "  1. 将 streamlit-iconify 添加到 requirements.txt"
echo "  2. 重新构建镜像: docker-compose build"
echo "  3. 或者进入容器安装:"
echo "     docker-compose exec streamlit pip install streamlit-iconify"
echo ""
echo "💡 提示：推荐将依赖添加到 requirements.txt，这样更规范"
echo ""
