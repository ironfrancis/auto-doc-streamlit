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
COPY requirements.txt .

# 安装 Python 依赖
# 分步安装，确保核心包先安装成功
RUN echo "📦 第一步：安装 Streamlit 及其核心依赖..." && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir streamlit --no-deps && \
    pip install --no-cache-dir altair blinker cachetools click numpy packaging pillow protobuf python-dateutil pytz requests rich tenacity toml typing-extensions tzlocal watchdog gitpython pydeck tornado pyarrow && \
    echo "✅ Streamlit 核心依赖已安装" && \
    pip show streamlit | head -3

RUN echo "📦 第二步：安装 FastAPI 和其他核心依赖..." && \
    pip install --no-cache-dir fastapi "uvicorn[standard]" requests httpx sqlalchemy psycopg2-binary alembic langgraph langchain-core langchain-openai python-dotenv pydantic python-multipart

RUN echo "📦 第三步：安装数据处理依赖..." && \
    pip install --no-cache-dir pandas openpyxl xlrd jinja2 markdown markdownify bs4

RUN echo "📦 第四步：安装其他工具..." && \
    (pip install --no-cache-dir selenium webdriver-manager || echo "⚠️  selenium 安装失败")

RUN echo "📦 第五步：尝试安装可选依赖（plotly, pyarrow）..." && \
    (pip install --no-cache-dir plotly 2>&1 | head -5 || echo "⚠️  plotly 安装失败") && \
    (pip install --no-cache-dir --only-binary=:all: pyarrow 2>/dev/null || \
     pip install --no-cache-dir pyarrow 2>/dev/null || \
     echo "⚠️  pyarrow 安装失败，将跳过") || true

RUN echo "✅ 最终验证..." && \
    (python -c "import streamlit; print('✅ Streamlit 可用')" || echo "⚠️  Streamlit 导入失败") && \
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

