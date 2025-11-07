# 🚀 AI内容创作与分发平台

> 现代化多容器架构的AI内容创作与管理平台，集成 FastAPI 后端、PostgreSQL 数据库和 LangGraph 工作流引擎。

---

## 🌟 主要特性

- **多容器架构**：Streamlit 前端 + FastAPI 后端 + PostgreSQL 数据库
- **LangGraph 工作流**：支持复杂的内容创作、多模型协作和智能审核优化流程
- **RESTful API**：完整的 REST API 接口，支持前端和第三方集成
- **数据持久化**：使用 PostgreSQL 存储数据，支持 JSONB 灵活配置
- **工作流状态管理**：支持工作流暂停、恢复、取消和历史查询
- **多频道AI写作**：支持多频道风格，自动联动多种大模型API
- **智能审核优化**：自动审核内容质量，多轮优化直到达到标准

---

## 🏗️ 架构说明

### 服务架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Streamlit  │────▶│   FastAPI   │────▶│ PostgreSQL  │
│   (前端)    │     │   (后端)    │     │  (数据库)   │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │
      │                    │
      └────────────────────┘
           LangGraph 工作流
```

### 目录结构

```
.
├── api/                    # FastAPI 后端应用
│   ├── main.py            # FastAPI 应用入口
│   ├── routers/           # API 路由
│   ├── services/          # 业务逻辑层
│   ├── database/          # 数据库配置和模型
│   └── graphs/            # LangGraph 工作流定义
│       ├── nodes/         # 工作流节点
│       ├── state.py       # 工作流状态定义
│       └── checkpointer.py # 状态持久化
├── pages/                  # Streamlit 页面
├── core/                   # 核心业务逻辑
├── config/                 # 配置文件
├── scripts/                # 工具脚本
│   └── migrate_json_to_db.py # 数据迁移脚本
├── docker-compose.yml      # Docker Compose 配置
├── Dockerfile              # Streamlit 服务镜像
└── Dockerfile.fastapi      # FastAPI 服务镜像
```

---

## 🚀 快速开始

### 前置要求

- **Docker** 和 **Docker Compose**（必需）
- 本项目使用 Docker 统一管理环境，**不需要本地 Python 环境**

### Docker 部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd Auto-doc-streamlit
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等
```

3. **启动服务**
```bash
# 使用启动脚本（推荐）
./start_project.sh

# 或使用 docker-start.sh
./docker-start.sh

# 或直接使用 docker-compose
docker-compose up -d

# 开发模式（热重载）
./start_project.sh --dev
```

4. **访问服务**
- Streamlit 前端：http://localhost:8501
- FastAPI 后端：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 数据迁移

如果从旧版本升级，需要迁移 JSON 数据到 PostgreSQL：

```bash
# 在容器内执行（推荐）
docker-compose exec fastapi python scripts/migrate_json_to_db.py
```

---

## 📚 API 文档

### 频道管理

- `GET /api/v1/channels` - 获取所有频道
- `POST /api/v1/channels` - 创建频道
- `PUT /api/v1/channels/{id}` - 更新频道
- `DELETE /api/v1/channels/{id}` - 删除频道

### 文章管理

- `GET /api/v1/articles` - 获取文章列表
- `POST /api/v1/articles` - 创建文章
- `PUT /api/v1/articles/{id}` - 更新文章
- `DELETE /api/v1/articles/{id}` - 删除文章

### 工作流管理

- `POST /api/v1/workflows/content-creation` - 启动内容创作工作流
- `POST /api/v1/workflows/multi-model` - 启动多模型协作工作流
- `POST /api/v1/workflows/optimization` - 启动智能审核优化工作流
- `GET /api/v1/workflows/{workflow_id}` - 获取工作流状态
- `POST /api/v1/workflows/{workflow_id}/continue` - 继续执行工作流
- `POST /api/v1/workflows/{workflow_id}/pause` - 暂停工作流
- `POST /api/v1/workflows/{workflow_id}/cancel` - 取消工作流

完整的 API 文档可在 http://localhost:8000/docs 查看。

---

## 🔄 LangGraph 工作流

### 内容创作工作流

多步骤、有状态的内容创作流程：

1. **输入收集** - 收集用户输入、频道配置、提示词块
2. **内容生成** - 使用指定 LLM 生成初稿
3. **质量检查** - 检查内容完整性、格式正确性
4. **内容优化** - 根据频道规则优化内容（条件分支）
5. **格式转换** - 转换为 Markdown/HTML
6. **输出保存** - 保存到数据库和文件系统

### 多模型协作工作流

不同模型处理不同任务的协作流程：

1. **任务分解** - 将复杂任务分解为子任务
2. **模型分配** - 为每个子任务选择最适合的模型
3. **并行执行** - 多个模型同时处理不同子任务
4. **结果整合** - 合并多个模型的结果
5. **一致性检查** - 确保结果的一致性

### 智能审核和优化流程

自动审核和优化的完整流程：

1. **内容生成** - 使用主模型生成内容
2. **质量审核** - 使用审核模型检查内容质量
3. **问题识别** - 识别需要优化的部分
4. **自动优化** - 根据审核结果自动优化内容
5. **二次审核** - 对优化后的内容进行二次审核
6. **发布决策** - 根据审核结果决定是否发布（条件分支）
7. **自动发布** - 通过审核后自动发布到指定频道

### 工作流状态管理

- **状态持久化**：工作流状态自动保存到 PostgreSQL
- **暂停/恢复**：支持工作流暂停和恢复执行
- **历史查询**：可以查询工作流的完整执行历史
- **错误处理**：自动记录错误信息，支持重试

---

## 🛠️ 开发指南

### 开发模式

使用开发模式启动，支持代码热重载：

```bash
# 开发模式（热重载）
./start_project.sh --dev

# 或使用 docker-compose
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### 数据库迁移

使用 Alembic 进行数据库迁移（在容器内执行）：

```bash
# 创建迁移
docker-compose exec fastapi alembic revision --autogenerate -m "描述"

# 应用迁移
docker-compose exec fastapi alembic upgrade head
```

---

## 📝 环境变量配置

创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/autodoc

# 项目路径
PROJECT_ROOT=/app
CONFIG_DIR=/app/config
WORKSPACE_DIR=/app/workspace

# 调试模式
DEBUG=True
```

---

## 🔧 故障排除

### 数据库连接失败

检查 PostgreSQL 服务是否运行：
```bash
docker-compose ps postgres
```

检查数据库连接字符串是否正确。

### 工作流执行失败

查看工作流执行历史：
```bash
GET /api/v1/workflows/{workflow_id}/history
```

检查日志：
```bash
docker-compose logs fastapi
```

---

## 📄 许可证

[添加许可证信息]

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
