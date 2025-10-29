# Anthropic 主题使用指南

## 📚 概述

我已经将 Anthropic 风格的大地色系主题提取为独立的 CSS 文件和 Python 工具，方便在整个应用中统一使用。

## 📁 文件结构

```
Auto-doc-streamlit/
├── static/
│   └── css/
│       └── anthropic_theme.css     # 主题 CSS 文件
├── core/
│   └── utils/
│       └── theme_loader.py          # 主题加载工具
├── homepage.py                      # 当前首页（内嵌CSS）
└── homepage_v2.py                   # 新版首页（使用外部CSS）
```

## 🚀 快速开始

### 方法 1：一行代码应用主题（推荐）

```python
from core.utils.theme_loader import apply_page_config

# 这一行代码完成页面配置 + 主题加载
apply_page_config(
    page_title="你的页面标题",
    page_icon="🎨"
)
```

### 方法 2：仅加载主题

```python
import streamlit as st
from core.utils.theme_loader import load_anthropic_theme

# 先配置页面
st.set_page_config(
    page_title="你的页面",
    page_icon="🎨",
    layout="wide"
)

# 然后加载主题
load_anthropic_theme()
```

## 🎨 使用主题组件

### 1. 页面标题

```python
from core.utils.theme_loader import create_page_title

create_page_title(
    title="频道管理",
    subtitle="统一管理所有发布频道"
)
```

### 2. 章节标题

```python
from core.utils.theme_loader import create_section_title

create_section_title("配置选项")
```

### 3. 信息面板

```python
from core.utils.theme_loader import create_info_panel

create_info_panel(
    title="功能特点",
    items=[
        "支持多种大语言模型",
        "智能对话管理",
        "数据安全保障"
    ]
)
```

### 4. 统计信息盒子

```python
from core.utils.theme_loader import create_stats_box

# 使用默认颜色
create_stats_box("100+", "用户数量")

# 使用特定颜色
create_stats_box("AI", "智能驱动", "card-gradient-2")
```

### 5. 提示面板

```python
from core.utils.theme_loader import (
    create_warning_panel,
    create_success_panel,
    create_error_panel
)

create_warning_panel("请注意：此操作不可撤销")
create_success_panel("操作成功完成")
create_error_panel("发生错误：无法连接到服务器")
```

## 📝 完整示例

创建一个新页面 `pages/13_Example_Page.py`：

```python
import streamlit as st
from core.utils.theme_loader import (
    apply_page_config,
    create_page_title,
    create_section_title,
    create_info_panel,
    create_stats_box
)

# 应用主题
apply_page_config(
    page_title="示例页面",
    page_icon="📚"
)

# 页面标题
create_page_title(
    title="示例页面",
    subtitle="演示如何使用 Anthropic 主题"
)

# 章节1
create_section_title("数据统计")

col1, col2, col3 = st.columns(3)
with col1:
    create_stats_box("150", "总用户数", "card-gradient-1")
with col2:
    create_stats_box("95%", "满意度", "card-gradient-2")
with col3:
    create_stats_box("24/7", "在线服务", "card-gradient-3")

# 章节2
create_section_title("功能介绍")

create_info_panel(
    title="核心特性",
    items=[
        "温暖的大地色系设计",
        "统一的视觉风格",
        "简单易用的API",
        "完全响应式布局"
    ]
)

# 正常的Streamlit组件也会自动匹配主题
st.write("这是普通的文本内容，会自动适配主题颜色。")
```

## 🎨 可用的CSS类

### 布局类

| 类名 | 用途 |
|------|------|
| `.main-title` | 主标题 |
| `.subtitle` | 副标题 |
| `.page-title` | 页面标题 |
| `.section-title` | 章节标题 |
| `.category-title` | 分类标题 |

### 卡片类

| 类名 | 用途 |
|------|------|
| `.card-container` | 卡片容器 |
| `.card-gradient-1` 到 `.card-gradient-8` | 8种大地色系渐变 |
| `.card-icon` | 卡片图标 |
| `.card-title` | 卡片标题 |
| `.card-description` | 卡片描述 |
| `.card-content` | 卡片内容区域 |

### 面板类

| 类名 | 用途 |
|------|------|
| `.info-panel` | 信息面板 |
| `.content-panel` | 内容面板 |
| `.warning-panel` | 警告面板 |
| `.success-panel` | 成功面板 |
| `.error-panel` | 错误面板 |

### 统计类

| 类名 | 用途 |
|------|------|
| `.stats-box` | 统计信息盒子 |
| `.stats-number` | 统计数字 |
| `.stats-label` | 统计标签 |

## 🎨 配色方案

### 主色系

```python
from core.utils.theme_loader import THEME_COLORS

THEME_COLORS = {
    "background": "#F5F1E8",      # 背景色（米黄色）
    "sidebar": "#FAFAF8",         # 侧边栏（浅米色）
    "primary_text": "#2B2B2B",    # 主文本（深灰黑）
    "secondary_text": "#6B6B6B",  # 副文本（中灰）
    "muted_text": "#5A5A5A",      # 柔和文本（灰）
    "accent": "#D97A5E",          # 强调色（赤陶橙）
}
```

### 大地色系渐变

```python
from core.utils.theme_loader import EARTH_COLORS

# 8种温暖的大地色系渐变
EARTH_COLORS = {
    "terra_cotta": {"light": "#E8957B", "dark": "#D97A5E"},  # 赤陶橙
    "warm_beige": {"light": "#D4C5B0", "dark": "#C4B19D"},   # 温暖米
    "soft_brown": {"light": "#C8B8A8", "dark": "#B5A393"},   # 浅棕
    "olive_brown": {"light": "#A3957F", "dark": "#8F8169"},  # 橄榄棕
    "warm_sand": {"light": "#D9B89A", "dark": "#C9A282"},    # 暖沙
    "cream": {"light": "#E5D4C1", "dark": "#D4C2AD"},        # 奶油
    "grey_brown": {"light": "#B8A89A", "dark": "#A89688"},   # 灰褐
    "cinnamon": {"light": "#CEB5A0", "dark": "#BDA38C"},     # 肉桂
}
```

## 🔄 迁移现有页面

### 步骤 1：添加导入

在页面顶部添加：

```python
from core.utils.theme_loader import apply_page_config
```

### 步骤 2：替换配置

将：

```python
st.set_page_config(
    page_title="我的页面",
    page_icon="🎨",
    layout="wide"
)
```

替换为：

```python
apply_page_config(
    page_title="我的页面",
    page_icon="🎨"
)
```

### 步骤 3：应用组件（可选）

使用主题组件替换标准HTML：

```python
# 之前
st.markdown("## 章节标题")

# 现在
create_section_title("章节标题")
```

## 📦 打包分发

如果你想在其他项目中使用这个主题：

1. **复制文件**：
   - `static/css/anthropic_theme.css`
   - `core/utils/theme_loader.py`

2. **调整路径**：
   在 `theme_loader.py` 中修改 CSS 文件路径

3. **安装依赖**：
   只需要 `streamlit`

## 🎯 最佳实践

### ✅ 推荐做法

1. **使用 `apply_page_config()`** - 一行代码完成配置
2. **使用主题组件** - 保持视觉一致性
3. **遵循配色方案** - 使用预定义的颜色
4. **保持简洁** - 避免过度自定义

### ❌ 避免

1. 不要混用多种风格的 CSS
2. 不要使用冲突的颜色
3. 不要重写主题的核心样式
4. 不要忘记加载主题

## 🆚 两个首页版本对比

| 特性 | homepage.py | homepage_v2.py |
|------|------------|----------------|
| **CSS位置** | 内嵌在文件中 | 外部CSS文件 |
| **代码长度** | ~567行 | ~250行 |
| **维护性** | 较低 | 高 |
| **复用性** | 低 | 高 |
| **推荐度** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 💡 建议

**对于新页面**：使用 `homepage_v2.py` 的方式
**对于现有页面**：逐步迁移到使用外部CSS

### 切换到新版本

```bash
# 备份当前版本
mv homepage.py homepage_old.py

# 使用新版本
mv homepage_v2.py homepage.py
```

## 📚 参考资源

- **CSS 文件**：`static/css/anthropic_theme.css`
- **工具函数**：`core/utils/theme_loader.py`
- **设计指南**：`DESIGN_GUIDE.md`
- **示例页面**：`homepage_v2.py`

---

**提示**：如果你在使用过程中遇到问题，请检查：
1. CSS 文件路径是否正确
2. 是否导入了正确的函数
3. 页面配置是否在加载主题之前

祝使用愉快！🎨

