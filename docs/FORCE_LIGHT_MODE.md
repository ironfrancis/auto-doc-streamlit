# 强制亮色模式设置指南

## 概述

本文档说明如何在应用中禁用暗黑模式，始终保持亮色主题。

## 设置方法

我们提供了**两种方法**来确保应用始终使用亮色模式：

### 方法1: Streamlit 配置文件（全局设置）

在项目根目录创建或修改 `.streamlit/config.toml` 文件：

```toml
[theme]
# 强制使用亮色主题
base = "light"
```

这个设置会：
- ✅ 对所有页面生效
- ✅ 禁用用户在设置中切换主题的功能
- ✅ 忽略系统的暗黑模式偏好

**配置文件位置**: `.streamlit/config.toml`

### 方法2: 代码层面控制（推荐）

在代码中使用 `force_light_mode` 参数：

```python
from core.utils.theme_loader import apply_page_config

# 强制使用亮色模式（默认行为）
apply_page_config(
    page_title="你的页面标题",
    page_icon="🚀",
    force_light_mode=True  # 默认就是True，可以省略
)
```

或者直接使用主题加载函数：

```python
from core.utils.theme_loader import load_anthropic_theme

# 强制亮色模式
load_anthropic_theme(force_light_mode=True)  # 默认True
```

## 工作原理

### 配置文件方式

- Streamlit 会读取 `.streamlit/config.toml` 文件
- `base = "light"` 设置会强制应用使用亮色主题
- 用户在UI中无法切换到暗黑模式

### 代码方式

当 `force_light_mode=True` 时，系统会自动添加以下CSS：

```css
/* 强制亮色模式 - 覆盖所有暗黑模式设置 */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    color-scheme: light !important;
}

/* 禁用系统暗黑模式偏好 */
@media (prefers-color-scheme: dark) {
    .stApp {
        background-color: #F5F1E8 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #FAFAF8 !important;
    }
}
```

这确保了：
- ✅ 即使系统设置为暗黑模式，应用仍显示亮色
- ✅ 覆盖所有可能的暗黑模式CSS规则
- ✅ 保持Anthropic风格的温暖配色

## 当前配置

项目当前的默认配置：

1. **配置文件**: `.streamlit/config.toml` 已设置为 `base = "light"` ✅
2. **代码默认**: `force_light_mode=True` ✅

这意味着**默认情况下，应用将始终显示亮色主题**。

## 如何允许暗黑模式（可选）

如果未来想要启用暗黑模式支持，需要：

### 1. 修改配置文件

```toml
[theme]
# 允许用户选择主题
# base = "light"  # 注释掉或删除这行
```

### 2. 修改代码

```python
# 允许暗黑模式
apply_page_config(
    page_title="你的页面标题",
    page_icon="🚀",
    force_light_mode=False  # 设置为False
)
```

## 验证设置

启动应用后：

1. 查看应用界面，应该显示温暖的米黄色背景
2. 打开系统设置，切换到暗黑模式
3. 刷新浏览器，应用应该保持亮色主题不变
4. 在Streamlit设置中，主题选项应该固定为亮色

## 相关文件

- `.streamlit/config.toml` - Streamlit全局配置
- `core/utils/theme_loader.py` - 主题加载器
- `static/css/anthropic_theme.css` - 主题CSS文件

## 注意事项

1. **配置文件优先级最高**：即使代码中设置 `force_light_mode=False`，如果配置文件设置了 `base = "light"`，应用仍会保持亮色
2. **重启应用**：修改配置文件后需要重启Streamlit应用才能生效
3. **缓存清理**：如果修改后没有生效，尝试清除浏览器缓存

## 配色方案参考

### 亮色模式配色

- 背景色: `#F5F1E8` (温暖米黄)
- 侧边栏: `#FAFAF8` (浅米色)
- 主标题: `#2B2B2B` (深灰黑)
- 副标题: `#6B6B6B` (中灰)
- 正文: `#5A5A5A` (柔和灰)
- 强调色: `#D97A5E` (赤陶橙)

这个配色方案灵感来自Anthropic和OpenAI的官网，营造温暖、专业的视觉体验。

## 更新日期

2025-10-21

