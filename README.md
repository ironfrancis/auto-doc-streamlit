# 🚀 AI内容创作与分发平台（纯Streamlit版）

> 高效、灵活、可扩展的AI内容创作与管理工具。无需后端，全部功能基于Streamlit实现。

---

## 🌟 主要亮点
- **多频道AI写作**：支持多频道风格，自动联动多种大模型API，高效内容生产
- **LLM端点注册与管理**：灵活注册、测试、切换多种大模型API，支持自定义参数
- **Markdown/HTML转换与历史**：本地MD审核、MD转HTML、历史记录与复用
- **智能图片处理**：自动下载网络图片到本地，复制本地图片到静态目录，确保离线可用
- **网页转写**：一键提取网页内容并转为Markdown
- **Token管理**：自动管理每个公众号的Token，支持自动读取、保存和更新
- **可视化界面**：基于Streamlit，操作简单，界面美观
- **多语言支持**：中英文界面一键切换

---

## 🛠️ 安装与启动

本项目支持三种主流依赖安装方式，任选其一即可：

### 1. pip
```bash
pip install -r requirements.txt
```

### 2. uv pip（推荐，速度更快）
```bash
pip install uv
uv pip install -r requirements.txt
```

### 3. uv sync（适合团队协作，需先生成 uv.lock 文件）
> 首次使用或依赖变更时，请先运行下方命令生成 uv.lock 文件：
```bash
pip install uv
uv pip compile requirements.txt
uv sync
```

### 启动平台

#### 方式一：使用统一启动脚本（推荐）
```bash
# 使用Python启动脚本
python3 start_app.py

# 或使用Shell启动脚本
./start.sh
```

#### 方式二：直接启动Streamlit
```bash
streamlit run app.py
```

---

## 🖼️ 图片处理功能

### 支持的图片类型
- **网络图片**：自动下载到本地，支持HTTP/HTTPS链接
- **本地图片**：自动复制到静态目录，支持绝对路径和相对路径
- **静态图片**：已存在的静态资源路径保持不变

### 图片处理流程
1. **网络图片下载**：自动下载并保存到 `app/static/images/` 目录
2. **本地图片复制**：将本地图片复制到静态目录
3. **路径更新**：自动更新Markdown中的图片路径为绝对路径
4. **HTML转换**：HTML中自动转换为Web可访问路径
5. **文件名管理**：自动生成唯一文件名，避免冲突

### 支持的图片格式
- PNG、JPG、JPEG、GIF、WebP

### 使用场景
#### 1. MD转HTML时的图片处理
在 `6_MD_to_HTML_Converter.py` 页面中，上传或粘贴Markdown内容时：
```markdown
# 网络图片（自动下载）
![网络图片](https://example.com/image.jpg)

# 本地图片（自动复制）
![本地图片](/Users/username/Desktop/photo.png)
![相对路径](./images/photo.jpg)

# 处理后的结果（使用绝对路径）
![网络图片](/Users/username/Projects/Auto-doc-streamlit/app/static/images/img_1703123456_a1b2c3d4.jpg)
![本地图片](/Users/username/Projects/Auto-doc-streamlit/app/static/images/photo_1.png)

# HTML中的结果（自动转换为Web路径）
<img src="/static/images/img_1703123456_a1b2c3d4.jpg" alt="网络图片">
<img src="/static/images/photo_1.png" alt="本地图片">
```

#### 2. Web转MD时的图片下载
在 `3_Web_to_MD.py` 页面中，从网页提取内容时：
- 启用 "Download Images to Local" 选项
- 网页中的图片会自动下载到本地
- Markdown内容中的图片路径会自动更新为绝对路径
- 图片保存在 `static/images/` 目录

---

## 📂 目录结构

```
📚 [项目文档](./docs/) - 详细的功能说明和使用指南
🚀 [主应用入口](./app.py) - Streamlit应用主入口文件
📄 [页面文件](./pages/) - Streamlit页面模块
⚙️ [配置目录](./config/) - 配置文件和模板信息
🛠️ [核心源码](./src/) - 核心业务逻辑和工具函数
📊 [静态资源](./static/) - CSS、图片等静态文件
📝 [模板文件](./templates/) - HTML模板文件
```