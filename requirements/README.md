# 项目依赖说明

## 依赖文件结构

本项目采用分离式依赖管理，针对不同的服务使用不同的依赖文件：

### 📁 依赖文件

- **`base.txt`** - 所有服务共用的基础依赖
  - HTTP客户端：requests, httpx
  - 配置管理：python-dotenv
  - 数据验证：pydantic
  - 数据处理：pandas, openpyxl, xlrd
  - 内容处理：jinja2, markdown, markdownify, bs4

- **`streamlit.txt`** - Streamlit前端服务专用依赖
  - 包含所有base.txt依赖
  - Streamlit框架及其UI组件
  - 可视化库：plotly, altair
  - 浏览器自动化：selenium

- **`fastapi.txt`** - FastAPI后端服务专用依赖
  - 包含所有base.txt依赖
  - FastAPI框架：fastapi, uvicorn
  - 数据库：sqlalchemy, psycopg2-binary, alembic
  - 工作流引擎：langgraph, langchain

- **`dev.txt`** - 开发环境依赖
  - 包含所有生产依赖
  - 测试工具：pytest, coverage
  - 代码质量：black, isort, flake8
  - 开发工具：jupyter, ipython

### 🐳 Docker构建

- **Streamlit容器**：使用 `requirements/streamlit.txt`
- **FastAPI容器**：使用 `requirements/fastapi.txt`
- **开发环境**：使用 `requirements/dev.txt`

### 📦 安装依赖

```bash
# 安装Streamlit前端依赖
pip install -r requirements/streamlit.txt

# 安装FastAPI后端依赖
pip install -r requirements/fastapi.txt

# 安装完整开发依赖
pip install -r requirements/dev.txt
```

### 🔄 依赖更新

1. 修改对应的requirements文件
2. 重新构建Docker镜像：
   ```bash
   docker-compose build --no-cache
   ```

### 💡 优化收益

- **镜像体积减少**：每个服务只安装必需依赖
- **构建速度提升**：依赖缓存命中率更高
- **维护性改善**：依赖边界清晰，版本管理精确
- **安全性提升**：减少不必要的依赖，降低安全风险