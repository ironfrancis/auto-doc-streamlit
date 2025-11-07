# Docker 迁移说明

本项目已完全迁移到 Docker 部署方式，不再需要本地 Python 环境和 uv 包管理器。

## ✅ 已清理的内容

1. **删除的文件**：
   - `uv.lock` - uv 锁定文件（已删除）

2. **更新的文件**：
   - `start_project.sh` - 重写为纯 Docker 启动脚本
   - `activate_env.sh` - 改为 Docker 环境说明脚本
   - `install_icons.sh` - 更新为 Docker 环境说明
   - `README.md` - 移除本地开发说明，强调 Docker 部署
   - `.gitignore` - 添加 `.venv/` 和 `uv.lock` 到忽略列表

3. **保留但不再使用的文件**：
   - `pyproject.toml` - 保留作为项目元数据（不依赖 uv）
   - `requirements.txt` - Docker 构建时使用

## 🗑️ 可选清理

如果确定不再需要本地开发环境，可以手动删除：

```bash
# 删除本地虚拟环境（如果存在）
rm -rf .venv/
rm -rf venv/
rm -rf env/
```

**注意**：这些目录已在 `.gitignore` 中，不会被提交到 Git。

## 🐳 Docker 使用方式

### 启动服务

```bash
# 标准启动
./start_project.sh

# 后台启动
./start_project.sh --detach

# 开发模式（热重载）
./start_project.sh --dev

# 重新构建并启动
./start_project.sh --build
```

### 查看日志

```bash
docker-compose logs -f
docker-compose logs -f streamlit  # 只看 Streamlit
docker-compose logs -f fastapi    # 只看 FastAPI
```

### 进入容器

```bash
# 进入 Streamlit 容器
docker-compose exec streamlit bash

# 进入 FastAPI 容器
docker-compose exec fastapi bash

# 在容器中执行命令
docker-compose exec fastapi python scripts/migrate_json_to_db.py
```

## 📦 依赖管理

所有 Python 依赖都在 Docker 构建时安装，通过 `requirements.txt` 管理：

1. **添加新依赖**：
   - 编辑 `requirements.txt`
   - 重新构建镜像：`docker-compose build`

2. **在容器中临时安装**：
   ```bash
   docker-compose exec streamlit pip install <package>
   ```
   （注意：容器重启后会丢失，建议添加到 requirements.txt）

## 💡 优势

- ✅ **环境一致性**：所有开发者使用相同的 Docker 环境
- ✅ **简化配置**：不需要管理本地 Python 版本和虚拟环境
- ✅ **更接近生产**：开发环境和生产环境一致
- ✅ **易于部署**：一键启动所有服务
- ✅ **隔离性**：不影响系统 Python 环境

## 🔄 从本地环境迁移

如果你之前使用本地虚拟环境：

1. **停止本地服务**（如果有运行）
2. **删除虚拟环境**（可选）：
   ```bash
   rm -rf .venv/
   ```
3. **使用 Docker 启动**：
   ```bash
   ./start_project.sh
   ```

## ❓ 常见问题

**Q: 我还能本地开发吗？**  
A: 可以，但推荐使用 Docker。如果必须本地开发，需要手动安装依赖，但项目不再维护本地环境配置。

**Q: 代码修改后需要重启吗？**  
A: 开发模式下不需要，代码会自动热重载。使用 `./start_project.sh --dev` 启动。

**Q: 如何调试？**  
A: 可以进入容器调试，或查看容器日志：`docker-compose logs -f`

