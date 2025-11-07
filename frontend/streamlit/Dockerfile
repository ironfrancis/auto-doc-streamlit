# Streamlit 前端应用 Dockerfile
FROM python:3.14-slim

# 设置工作目录
WORKDIR /app

# 配置 Debian 镜像源（使用清华大学镜像）
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

# 安装系统依赖
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    gcc g++ curl wget gnupg unzip cmake make build-essential \
    libssl-dev libffi-dev pkg-config ninja-build \
    ca-certificates fonts-liberation libappindicator3-1 \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 \
    libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 \
    libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 \
    libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 \
    libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 \
    libxrender1 libxss1 libxtst6 lsb-release xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 安装浏览器（根据架构选择）
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg && \
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
        apt-get update && apt-get install -y google-chrome-stable && rm -rf /var/lib/apt/lists/*; \
    else \
        apt-get update && apt-get install -y chromium chromium-driver && rm -rf /var/lib/apt/lists/* && \
        ln -s /usr/bin/chromium /usr/bin/google-chrome-stable; \
    fi

# 配置 pip 镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖（分步安装避免 pyarrow 问题）
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir streamlit --no-deps && \
    pip install --no-cache-dir requests httpx python-dotenv pydantic python-multipart && \
    pip install --no-cache-dir jinja2 markdown markdownify bs4 && \
    pip install --no-cache-dir cachetools click numpy packaging pillow protobuf python-dateutil pytz rich tenacity toml typing-extensions tzlocal pydeck tornado selenium webdriver-manager blinker && \
    pip install --no-cache-dir gitpython altair watchdog plotly || true

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 启动命令
CMD ["python", "-m", "streamlit", "run", "homepage.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=watchdog", "--server.runOnSave=true"]