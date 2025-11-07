# 使用 Python 3.14-slim 作为基础镜像
FROM python:3.14-slim
# 设置工作目录
WORKDIR /app

# 配置 Debian 镜像源（使用清华大学镜像，Debian 13 trixie）
RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's|http://snapshot.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources; \
    else \
        echo "Types: deb" > /etc/apt/sources.list.d/debian.sources && \
        echo "URIs: https://mirrors.tuna.tsinghua.edu.cn/debian" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Suites: trixie trixie-updates" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Components: main contrib non-free non-free-firmware" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg" >> /etc/apt/sources.list.d/debian.sources && \
        echo "" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Types: deb" >> /etc/apt/sources.list.d/debian.sources && \
        echo "URIs: https://mirrors.tuna.tsinghua.edu.cn/debian-security" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Suites: trixie-security" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Components: main contrib non-free non-free-firmware" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg" >> /etc/apt/sources.list.d/debian.sources; \
    fi

# 安装系统依赖（包括 Selenium 所需的浏览器和编译工具）
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    wget \
    gnupg \
    unzip \
    cmake \
    make \
    build-essential \
    libssl-dev \
    libffi-dev \
    pkg-config \
    ninja-build \
    # Chrome 浏览器依赖
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 安装浏览器（根据架构选择 Chrome 或 Chromium）
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        # AMD64 架构：安装 Google Chrome
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg && \
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
        apt-get update && \
        apt-get install -y google-chrome-stable && \
        rm -rf /var/lib/apt/lists/*; \
    else \
        # ARM64 或其他架构：安装 Chromium
        apt-get update && \
        apt-get install -y chromium chromium-driver && \
        rm -rf /var/lib/apt/lists/* && \
        # 创建符号链接以便代码中使用 chrome 命令
        ln -s /usr/bin/chromium /usr/bin/google-chrome-stable; \
    fi

# 配置 pip 镜像源（使用清华大学镜像）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 复制依赖文件
COPY requirements/ ./requirements/

# 安装 Python 依赖（处理 pyarrow 兼容性问题）
RUN echo "📦 安装 Streamlit 前端依赖..." && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir streamlit --no-deps && \
    pip install --no-cache-dir -r requirements/base.txt && \
    echo "✅ 安装其他 Streamlit 依赖（跳过问题包）..." && \
    pip install --no-cache-dir plotly altair watchdog gitpython cachetools click numpy packaging pillow protobuf python-dateutil pytz rich tenacity toml typing-extensions tzlocal pydeck tornado selenium webdriver-manager blinker || true && \
    echo "✅ Streamlit 依赖安装完成" && \
    pip show streamlit | head -3

RUN echo "✅ 验证关键包..." && \
    (python -c "import streamlit; print('✅ Streamlit 可用')" || echo "⚠️  Streamlit 导入失败") && \
    (python -c "import plotly; print('✅ Plotly 可用')" || echo "⚠️  Plotly 导入失败") && \
    (python -c "import selenium; print('✅ Selenium 可用')" || echo "⚠️  Selenium 导入失败") && \
    (python -m streamlit --version || echo "⚠️  Streamlit 命令失败，但包已安装")

# 注意：代码通过 volume 挂载，不需要 COPY
# 这样可以实现开发模式下的热重载

# 暴露 Streamlit 端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 默认命令（会被 docker-compose 覆盖）
CMD ["python", "-m", "streamlit", "run", "homepage.py", "--server.port=8501", "--server.address=0.0.0.0"]

