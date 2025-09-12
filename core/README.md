# Core 模块说明文档

## 📁 目录结构概览

`core/` 目录是AI内容创作平台的核心功能模块，包含所有核心业务逻辑和工具函数。

```
core/
├── README.md                    # 本文档
├── __init__.py                 # 核心模块入口，导出所有主要功能
├── crawlers/                   # 🕷️ 数据采集模块
├── processors/                 # ⚙️ 内容处理模块  
├── channel/                    # 📺 频道管理模块
├── utils/                      # 🛠️ 通用工具模块
├── web2md/                     # 🌐 网页转Markdown模块
└── wechat/                     # 📱 微信相关功能模块
```

## 🔍 详细模块说明

### 1. 🕷️ `crawlers/` - 数据采集模块

专门负责从各种网站采集数据，包括文章、新闻、技术资讯等。

#### `source_53ai.py`
- **功能**: 53AI网站文章爬虫
- **用途**: 自动采集53AI网站的技术文章、AI新闻、行业资讯
- **特点**: 
  - 支持分页爬取
  - 自动提取文章标题、内容、发布时间
  - 智能过滤无关内容
  - 支持CSV导出

#### `toutiao_api.py`
- **功能**: 今日头条API数据采集
- **用途**: 通过头条API获取文章数据，包括阅读量、点赞数、评论数等
- **特点**:
  - 支持批量获取文章信息
  - 自动去重和更新
  - 数据同步到发布历史

### 2. ⚙️ `processors/` - 内容处理模块

负责对采集到的内容进行处理、优化和格式化。

#### `article_info_processor.py`
- **功能**: 文章信息处理器
- **用途**: 从掘金等平台提取文章的关键信息
- **特点**:
  - 支持多种内容平台
  - 提取标题、作者、发布时间、阅读量等
  - 支持Playwright动态渲染

### 3. 📺 `channel/` - 频道管理模块

管理内容发布频道，包括频道配置、提示词块管理等。

#### `channel_management.py`
- **功能**: 频道管理核心
- **用途**: 频道的CRUD操作、数据验证、配置管理
- **特点**:
  - 支持频道创建、编辑、删除、复制
  - 自动时间戳管理
  - 数据验证和错误处理

#### `channel_update_manager.py`
- **功能**: 频道更新管理器
- **用途**: 批量更新频道数据，检查Cookie状态
- **特点**:
  - 支持批量操作
  - Cookie状态监控
  - 错误处理和日志记录

#### `prompt_block_management.py`
- **功能**: 提示词块管理（增强版）
- **用途**: 管理提示词块的读取、组合和生成
- **特点**:
  - 支持分类管理（public/industry/custom）
  - 智能组合提示词
  - 数据格式转换

#### `prompt_block_manager.py`
- **功能**: 提示词块管理器（基础版）
- **用途**: 提示词块的基础CRUD操作
- **特点**:
  - 简单的块管理
  - JSON格式支持
  - 统计信息

### 4. 🛠️ `utils/` - 通用工具模块

提供各种辅助功能和工具函数。

#### `calendar_visualizer.py`
- **功能**: 日历可视化工具
- **用途**: 创建发布日历的热力图、月度视图、时间线等
- **特点**:
  - 多种可视化方式
  - 支持频道筛选
  - 发布模式分析

#### `data_operations.py`
- **功能**: 数据操作功能
- **用途**: 端点信息加载、模板文件管理、数据导入导出
- **特点**:
  - 支持多种数据格式
  - 自动备份和恢复
  - 数据统计

#### `language_manager.py`
- **功能**: 语言管理器
- **用途**: 多语言支持，中英文切换
- **特点**:
  - 统一的文本字典
  - 语言选择器
  - 国际化支持

#### `markdown_to_wx.py`
- **功能**: Markdown转微信格式
- **用途**: 将Markdown内容转换为微信公众号兼容的HTML
- **特点**:
  - 代码高亮支持
  - 微信样式优化
  - 脚注自动生成

#### `md_utils.py`
- **功能**: Markdown工具集
- **用途**: Markdown处理、HTML转换、图片处理
- **特点**:
  - 多种模板支持
  - 图片自动下载和转换
  - 样式优化

#### `navigation_manager.py`
- **功能**: 导航管理器
- **用途**: 页面导航、功能卡片渲染
- **特点**:
  - 动态导航生成
  - 多语言支持
  - 分类管理

#### `path_manager.py`
- **功能**: 路径管理器
- **用途**: 统一管理所有数据路径，支持workspace和legacy路径
- **特点**:
  - 智能路径检测
  - 目录自动创建
  - 路径验证

#### `review_ui.py`
- **功能**: 审核UI界面
- **用途**: 内容审核的用户界面
- **特点**:
  - 响应式设计
  - 多语言支持
  - 功能卡片展示

#### `token_manager.py`
- **功能**: Token管理器
- **用途**: 管理微信公众号的Token信息
- **特点**:
  - 自动过期检测
  - 状态监控
  - 配置备份

#### `ui_components.py`
- **功能**: UI组件库
- **用途**: 可复用的UI组件，如表单、对话框等
- **特点**:
  - 组件化设计
  - 高度可定制
  - 统一风格

### 5. 🌐 `web2md/` - 网页转Markdown模块

专门负责将网页内容转换为Markdown格式。

#### `enhanced_web2md.py`
- **功能**: 增强版网页转Markdown
- **用途**: 使用MagicLens从网页提取Markdown内容
- **特点**:
  - 支持滚动加载
  - 图片自动下载
  - 多种提取范围
  - 干扰元素移除

#### `gzh_url2md.py`
- **功能**: 公众号URL转Markdown
- **用途**: 专门处理微信公众号文章链接
- **特点**:
  - 针对微信优化
  - AI内容优化
  - 图片链接修复

#### `web2md.py`
- **功能**: 基础网页转Markdown
- **用途**: 简单的网页内容提取
- **特点**:
  - 轻量级实现
  - 基础功能
  - 易于使用

### 6. 📱 `wechat/` - 微信相关功能模块

专门处理微信公众号相关的功能。

#### `cookie_manager.py`
- **功能**: Cookie管理器
- **用途**: 管理微信公众号的登录Cookie信息
- **特点**:
  - 自动过期检测
  - 状态监控
  - 多账号支持

#### `wechat_article_scraper.py`
- **功能**: 微信文章抓取器
- **用途**: 从微信公众号文章URL获取发布信息
- **特点**:
  - 自动信息提取
  - 批量处理
  - 错误处理

#### `wechat_data_processor.py`
- **功能**: 微信数据处理工具
- **用途**: 处理微信公众号导出的Excel数据文件
- **特点**:
  - Excel文件处理
  - 数据合并去重
  - CSV导出

## 🔧 使用方式

### 导入模块
```python
# 导入所有核心功能
from core import *

# 导入特定模块
from core.crawlers import Source53AI
from core.processors import extract_article_info
from core.channel import ChannelManager
from core.utils import md_to_html
from core.web2md import extract_markdown_from_url
from core.wechat import CookieManager
```

### 常用功能示例
```python
# 爬取53AI文章
crawler = Source53AI()
articles = crawler.crawl_articles(5)

# 处理文章信息
info = extract_article_info(html_content)

# 管理频道
channel_mgr = ChannelManager()
channels = channel_mgr.get_all_channels()

# 转换网页为Markdown
md_content = extract_markdown_from_url("https://example.com")

# 管理微信Cookie
cookie_mgr = CookieManager()
status = cookie_mgr.get_cookie_status("AGI观察室")
```

## 📋 依赖关系

- **基础依赖**: `requests`, `pandas`, `beautifulsoup4`
- **Web自动化**: `selenium`, `playwright`
- **数据处理**: `markdown`, `jinja2`
- **可视化**: `plotly`, `streamlit`

## 🚀 扩展指南

### 添加新的爬虫
1. 在 `crawlers/` 目录下创建新文件
2. 实现标准的爬虫接口
3. 在 `crawlers/__init__.py` 中导出

### 添加新的处理器
1. 在 `processors/` 目录下创建新文件
2. 实现处理逻辑
3. 在 `processors/__init__.py` 中导出

### 添加新的工具
1. 在 `utils/` 目录下创建新文件
2. 实现工具函数
3. 在 `utils/__init__.py` 中导出

## 📝 注意事项

1. **路径管理**: 所有文件路径都应通过 `path_manager` 统一管理
2. **错误处理**: 每个模块都应包含完善的错误处理机制
3. **日志记录**: 重要操作应记录日志
4. **配置管理**: 敏感信息应通过配置文件管理
5. **测试覆盖**: 新功能应包含相应的测试用例

## 🔄 更新日志

- **v1.0.0**: 初始版本，基础功能模块
- **v1.1.0**: 重构目录结构，优化模块组织
- **v1.2.0**: 添加爬虫和处理器模块
- **v1.3.0**: 完善工具模块和文档

---

*本文档会随着模块的更新而持续维护，如有疑问请查看具体模块的代码注释或联系开发团队。*
