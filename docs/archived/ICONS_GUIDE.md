# 使用 Icônes 图标库指南

## 📚 关于 Icônes

[Icônes](https://icones.js.org/) 是一个包含超过 200,000+ 个开源图标的集合，包括：
- **Material Design Icons** - Google 设计的图标
- **Phosphor Icons** - 优雅的图标系列
- **Carbon Icons** - IBM 设计系统
- **Feather Icons** - 简洁的图标
- **Lucide** - Feather 的改进版
- **Iconoir** - 手绘风格图标
- 以及更多...

## 🎯 推荐图标集

根据 Anthropic 风格，推荐使用以下图标集：

### 1. **Phosphor Icons**（最推荐）
- 风格：优雅、现代、手绘感
- 适合：Anthropic 风格的温暖设计
- 网址：搜索 "phosphor" 在 https://icones.js.org/

### 2. **Iconoir**
- 风格：手绘线条，简洁优雅
- 适合：温暖、人性化的设计
- 网址：搜索 "iconoir" 在 https://icones.js.org/

### 3. **Lucide**
- 风格：清晰、现代
- 适合：专业的界面设计
- 网址：搜索 "lucide" 在 https://icones.js.org/

## 🚀 使用方法

### 方法 1: 使用 Iconify（推荐）

安装 streamlit-iconify：
```bash
pip install streamlit-iconify
```

然后在代码中使用：
```python
from streamlit_iconify import iconify

iconify("ph:robot", color="#2B2B2B", width=45)
```

### 方法 2: 直接使用 SVG

1. 访问 https://icones.js.org/
2. 搜索你需要的图标（例如 "robot"）
3. 点击图标，选择 "Copy SVG"
4. 在代码中使用：

```python
st.markdown("""
<div class="card-icon">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
        <path d="..." fill="currentColor"/>
    </svg>
</div>
""", unsafe_allow_html=True)
```

### 方法 3: 使用 Data URL

```python
icon_data_url = "data:image/svg+xml;base64,..."
st.markdown(f"""
<div class="card-icon">
    <img src="{icon_data_url}" alt="icon"/>
</div>
""", unsafe_allow_html=True)
```

## 📋 为首页功能推荐的图标

基于 Phosphor Icons 的推荐：

| 功能 | 推荐图标 | Iconify 代码 |
|------|----------|--------------|
| AI内容创作 | `ph:robot` | `iconify("ph:robot")` |
| 网页转MD | `ph:globe` | `iconify("ph:globe")` |
| MD转HTML | `ph:file-html` | `iconify("ph:file-html")` |
| 频道管理 | `ph:broadcast` | `iconify("ph:broadcast")` |
| 发布历史 | `ph:chart-line` | `iconify("ph:chart-line")` |
| 发布日历 | `ph:calendar` | `iconify("ph:calendar")` |
| LLM端点 | `ph:plugs` | `iconify("ph:plugs")` |
| 信息源注册 | `ph:notebook` | `iconify("ph:notebook")` |
| 模板管理 | `ph:paint-brush` | `iconify("ph:paint-brush")` |
| AI布局 | `ph:layout` | `iconify("ph:layout")` |
| 图片搜索 | `ph:image` | `iconify("ph:image")` |
| 数据上传 | `ph:upload` | `iconify("ph:upload")` |

## 🎨 样式建议

为了匹配 Anthropic 风格，建议使用以下样式：

```css
.card-icon svg {
    width: 2.8rem;
    height: 2.8rem;
    color: #2B2B2B;  /* 深灰色，不是纯黑 */
    opacity: 0.85;    /* 稍微透明，更柔和 */
    stroke-width: 1.5; /* 线条粗细 */
}
```

## 💡 实际应用示例

### 使用 streamlit-iconify（最简单）

```python
from streamlit_iconify import iconify

# 在卡片中使用
st.markdown("""
<div class="card-container card-gradient-1">
    <div class="card-icon">
""", unsafe_allow_html=True)

# 插入图标
iconify("ph:robot", color="#2B2B2B", width=45)

st.markdown("""
    </div>
    <div class="card-content">
        <div class="card-title">AI内容创作与转写</div>
        <div class="card-description">使用AI辅助创作内容...</div>
    </div>
</div>
""", unsafe_allow_html=True)
```

### 纯 HTML/CSS 方案

创建一个图标映射字典：

```python
ICONS = {
    "robot": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
        <path d="M200,48H136V16a8,8,0,0,0-16,0V48H56A32,32,0,0,0,24,80V192a32,32,0,0,0,32,32H200a32,32,0,0,0,32-32V80A32,32,0,0,0,200,48ZM40,192V80A16,16,0,0,1,56,64H200a16,16,0,0,1,16,16V192a16,16,0,0,1-16,16H56A16,16,0,0,1,40,192Zm76-68a12,12,0,1,1-12-12A12,12,0,0,1,116,124Zm72,0a12,12,0,1,1-12-12A12,12,0,0,1,188,124Zm-12,32H80a8,8,0,0,0-6.74,12.28,72,72,0,0,0,109.48,0A8,8,0,0,0,176,156Z" fill="currentColor"/>
    </svg>""",
    # ... 更多图标
}

# 使用
st.markdown(f"""
<div class="card-icon">
    {ICONS['robot']}
</div>
""", unsafe_allow_html=True)
```

## 🔍 如何选择合适的图标

1. **访问** https://icones.js.org/
2. **选择图标集**：推荐 Phosphor, Iconoir, Lucide
3. **搜索关键词**：输入功能相关的英文词
4. **预览**：查看图标是否符合你的风格
5. **复制**：选择 "Copy SVG" 或 "Copy Iconify"
6. **应用**：粘贴到你的代码中

## 📦 快速开始

最简单的方法是使用 streamlit-iconify：

```bash
# 安装
pip install streamlit-iconify

# 在 requirements.txt 中添加
echo "streamlit-iconify" >> requirements.txt
```

然后修改 homepage.py：

```python
from streamlit_iconify import iconify

# 替换 emoji
# 之前: <div class="card-icon">🤖</div>
# 之后:
st.markdown('<div class="card-icon">', unsafe_allow_html=True)
iconify("ph:robot", color="#2B2B2B", width=45)
st.markdown('</div>', unsafe_allow_html=True)
```

## 🎯 优势

相比 emoji：
- ✅ 更专业、更统一的视觉风格
- ✅ 可自定义颜色、大小、粗细
- ✅ 更符合 Anthropic 的手绘风格
- ✅ 跨平台显示一致
- ✅ 更现代的设计感

## 📚 参考资源

- **Icônes 官网**: https://icones.js.org/
- **Phosphor Icons**: https://phosphoricons.com/
- **Iconoir**: https://iconoir.com/
- **Lucide**: https://lucide.dev/
- **streamlit-iconify**: https://github.com/streamlit/streamlit-iconify

---

**提示**：如果你想要我帮你实现图标替换，请告诉我你想使用哪个方案（streamlit-iconify 或纯 SVG）！

