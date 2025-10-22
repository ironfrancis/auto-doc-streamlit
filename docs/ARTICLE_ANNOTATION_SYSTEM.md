# 文章批注系统技术文档

## 📋 目录

1. [系统概述](#系统概述)
2. [技术架构](#技术架构)
3. [核心组件](#核心组件)
4. [使用指南](#使用指南)
5. [API 参考](#api-参考)
6. [数据结构](#数据结构)
7. [维护指南](#维护指南)
8. [故障排查](#故障排查)

---

## 系统概述

### 功能简介

文章批注系统是一个基于 JavaScript 的前端批注工具，集成在 WriteArena 页面中，用于对 AI 生成的文章进行质量评审和批注标记。

### 核心特性

- ✅ **文本选择高亮** - 鼠标选择文本后可以高亮标记
- ✅ **批注分类** - 支持5种批注类型（语言、事实、内容、风格、格式）
- ✅ **严重程度** - 三个级别（低、中、高）
- ✅ **批注管理** - 添加、查看、删除批注
- ✅ **数据持久化** - 批注数据保存到并发历史 JSON 文件
- ✅ **可视化展示** - 不同严重程度用不同颜色标识

### 应用场景

1. **模型质量评估** - 标记 AI 生成内容的问题
2. **提示词优化** - 记录需要改进的地方
3. **A/B 测试** - 对比不同模型的输出质量
4. **知识积累** - 建立模型质量数据库

---

## 技术架构

### 整体架构图

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit 前端                      │
│  (WriteArena 页面 - 13_WriteArena.py)               │
├─────────────────────────────────────────────────────┤
│                     组件层                           │
│  ┌──────────────┐        ┌──────────────┐          │
│  │ HTML 容器    │◄──────►│ JavaScript   │          │
│  │ (文章展示)   │        │ 批注引擎     │          │
│  └──────────────┘        └──────────────┘          │
├─────────────────────────────────────────────────────┤
│                   通信层                             │
│        postMessage API (双向通信)                   │
├─────────────────────────────────────────────────────┤
│                   数据层                             │
│  ┌──────────────────────────────────────┐          │
│  │ workspace/concurrent_history/         │          │
│  │ {task_id}_{channel}.json              │          │
│  │   ├─ results                          │          │
│  │   ├─ judgments                        │          │
│  │   └─ annotations ← 批注数据           │          │
│  └──────────────────────────────────────┘          │
└─────────────────────────────────────────────────────┘
```

### 文件结构

```
Auto-doc-streamlit/
├── static/
│   └── js/
│       └── article_annotator.js       # 批注 JS 库（新增）
├── pages/
│   └── 13_WriteArena.py               # WriteArena 页面（需修改）
├── workspace/
│   └── concurrent_history/
│       └── *.json                     # 批注数据存储
└── docs/
    └── ARTICLE_ANNOTATION_SYSTEM.md   # 本文档
```

---

## 核心组件

### 1. ArticleAnnotator 类

JavaScript 批注引擎的核心类。

#### 初始化

```javascript
const annotator = new ArticleAnnotator('article-content', {
    highlightColor: '#fff59d',    // 批注高亮颜色
    selectedColor: '#ffeb3b',     // 选中批注颜色
    readOnly: false               // 是否只读模式
});
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `containerId` | string | - | 文章容器的 DOM ID（必填） |
| `options.highlightColor` | string | `#fff59d` | 批注背景色（黄色） |
| `options.selectedColor` | string | `#ffeb3b` | 选中时的背景色 |
| `options.readOnly` | boolean | `false` | 只读模式（不可添加批注） |

### 2. 工作流程

#### 添加批注流程

```
1. 用户选择文本
    ↓
2. 显示批注工具栏
    ↓
3. 用户填写批注信息
    - 类型：语言/事实/内容/风格/格式
    - 严重程度：低/中/高
    - 批注内容：文字说明
    ↓
4. 保存批注
    ↓
5. 高亮文本（添加 <span> 包裹）
    ↓
6. 通知 Streamlit（postMessage）
    ↓
7. Python 保存到 JSON 文件
```

#### 查看批注流程

```
1. 点击高亮的文本
    ↓
2. 切换高亮颜色（视觉反馈）
    ↓
3. 通知 Streamlit 显示详情
    ↓
4. 侧边栏显示批注详情
```

---

## 使用指南

### 在 WriteArena 中集成

#### 步骤 1: 修改 WriteArena 页面

在 `pages/13_WriteArena.py` 中添加批注组件：

```python
import streamlit as st
import streamlit.components.v1 as components

# ... 现有代码 ...

# 在显示文章内容的地方
if article_content:
    # 创建批注容器
    annotation_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;
                line-height: 1.8;
                padding: 20px;
                color: #2B2B2B;
            }}
            
            #article-content {{
                max-width: 800px;
                margin: 0 auto;
            }}
            
            /* 批注高亮样式由 JS 动态添加 */
        </style>
    </head>
    <body>
        <div id="article-content">
            {article_content}
        </div>
        
        <!-- 引入批注 JS -->
        <script src="/static/js/article_annotator.js"></script>
        <script>
            // 初始化批注工具
            const annotator = new ArticleAnnotator('article-content', {{
                highlightColor: '#fff59d',
                selectedColor: '#ffeb3b',
                readOnly: false
            }});
            
            // 加载已有批注（如果有）
            const existingAnnotations = {existing_annotations_json};
            if (existingAnnotations) {{
                annotator.loadAnnotations(existingAnnotations);
            }}
            
            // 监听 Streamlit 的数据变化
            window.addEventListener('message', function(event) {{
                if (event.data.type === 'streamlit:render') {{
                    // Streamlit 重新渲染时的处理
                }
            }});
        </script>
    </body>
    </html>
    """
    
    # 渲染 HTML
    components.html(annotation_html, height=800, scrolling=True)
```

#### 步骤 2: 处理批注数据

```python
# 在页面的 Python 代码中

# 监听来自 JavaScript 的消息
component_value = components.html(annotation_html, height=800, scrolling=True)

if component_value:
    # 处理批注事件
    if component_value.get('type') == 'annotation_added':
        annotation = component_value.get('annotation')
        all_annotations = component_value.get('all_annotations')
        
        # 保存到 session_state
        if 'annotations' not in st.session_state:
            st.session_state.annotations = {}
        
        st.session_state.annotations[endpoint_name] = all_annotations
        
        # 保存到文件
        save_annotations_to_file(task_id, endpoint_name, all_annotations)
        
        st.success(f"批注已保存：{annotation['type']} - {annotation['severity']}")
```

#### 步骤 3: 数据持久化

```python
def save_annotations_to_file(task_id, endpoint_name, annotations):
    """保存批注到并发历史 JSON 文件"""
    history_dir = get_concurrent_history_dir()
    json_path = os.path.join(history_dir, f"{task_id}_*.json")
    
    # 读取现有文件
    import glob
    files = glob.glob(json_path)
    if files:
        file_path = files[0]
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加批注数据
        if 'annotations' not in data:
            data['annotations'] = {}
        
        data['annotations'][endpoint_name] = annotations
        
        # 保存
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
```

### 基本操作

#### 添加批注

1. **选择文本**：用鼠标拖动选择要批注的文本
2. **填写信息**：
   - 选择批注类型（5种可选）
   - 选择严重程度（低/中/高）
   - 输入批注内容
3. **保存**：点击"保存"按钮

#### 查看批注

- 点击高亮的文本，侧边栏会显示批注详情

#### 删除批注

```python
# 在 Streamlit 侧边栏添加删除按钮
if st.button("删除此批注"):
    # 调用 JavaScript 删除方法
    components.html("""
        <script>
            window.annotator.deleteAnnotation('{annotation_id}');
        </script>
    """)
```

---

## API 参考

### JavaScript API

#### 构造函数

```javascript
new ArticleAnnotator(containerId, options)
```

#### 方法

##### loadAnnotations(annotations)

加载已有的批注数据。

```javascript
const annotations = [
    {
        id: 'anno_123',
        quote: '选中的文本',
        type: 'language',
        severity: 'medium',
        content: '批注内容',
        created_at: '2024-10-22T10:30:00Z'
    }
];

annotator.loadAnnotations(annotations);
```

##### getAnnotations()

获取所有批注数据。

```javascript
const allAnnotations = annotator.getAnnotations();
console.log(allAnnotations);
```

##### deleteAnnotation(annotationId)

删除指定批注。

```javascript
annotator.deleteAnnotation('anno_123');
```

##### exportAnnotations()

导出批注数据为 JSON 字符串。

```javascript
const jsonString = annotator.exportAnnotations();
// 可以复制或下载
```

##### destroy()

销毁批注工具（移除所有高亮和事件监听）。

```javascript
annotator.destroy();
```

### Python API

#### 保存批注

```python
def save_annotations_to_file(task_id, endpoint_name, annotations):
    """
    保存批注到文件
    
    参数:
        task_id: 任务ID
        endpoint_name: 端点名称
        annotations: 批注数组
    """
    # 实现代码见上文
```

#### 加载批注

```python
def load_annotations_from_file(task_id, endpoint_name):
    """
    从文件加载批注
    
    返回:
        批注数组
    """
    history_dir = get_concurrent_history_dir()
    # ... 读取逻辑
    return annotations
```

---

## 数据结构

### 批注对象

```json
{
  "id": "anno_1634567890123_abc123",
  "quote": "选中的文本片段",
  "type": "language",
  "severity": "medium",
  "content": "这里的表达不够准确，建议改为...",
  "created_at": "2024-10-22T10:30:00.123Z",
  "position": {
    "startOffset": 120,
    "endOffset": 135,
    "startContainer": [0, 1, 2],
    "endContainer": [0, 1, 2]
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|-----|------|------|
| `id` | string | 唯一标识符（自动生成） |
| `quote` | string | 被批注的文本片段 |
| `type` | string | 批注类型（见下表） |
| `severity` | string | 严重程度（low/medium/high） |
| `content` | string | 批注内容（用户输入） |
| `created_at` | string | 创建时间（ISO 8601 格式） |
| `position` | object | 文本位置信息（用于重新定位） |

### 批注类型

| 值 | 图标 | 说明 |
|----|-----|------|
| `language` | 📝 | 语言问题（语法、表达、逻辑） |
| `fact` | 📊 | 事实错误（数据、引用） |
| `content` | 💡 | 内容建议（结构、深度、案例） |
| `style` | ⚠️ | 风格问题（语气、专业度） |
| `format` | 🔧 | 格式问题（Markdown 语法） |

### JSON 文件结构

```json
{
  "id": "20251022_174704",
  "channel": "AGI启示录",
  "timestamp": "2025-10-22 17:47:45",
  "results": [/* 端点结果 */],
  "judgments": {/* 评判数据 */},
  
  "annotations": {
    "Magic Claude": [
      {
        "id": "anno_001",
        "quote": "AI技术发展迅速",
        "type": "fact",
        "severity": "medium",
        "content": "太笼统，建议加具体数据",
        "created_at": "2024-10-22T18:30:00Z"
      },
      {
        "id": "anno_002",
        "quote": "未来展望",
        "type": "content",
        "severity": "low",
        "content": "可以加入更多案例",
        "created_at": "2024-10-22T18:32:00Z"
      }
    ],
    "Magic GPT5": [/* 其他端点的批注 */]
  }
}
```

---

## 维护指南

### 修改批注类型

在 `article_annotator.js` 的工具栏创建函数中修改：

```javascript
// 找到这部分代码（约第 100 行）
<select id="annotation-type">
    <option value="language">📝 语言问题</option>
    <option value="fact">📊 事实错误</option>
    <option value="content">💡 内容建议</option>
    <option value="style">⚠️ 风格问题</option>
    <option value="format">🔧 格式问题</option>
    <!-- 添加新类型 -->
    <option value="newtype">🆕 新类型</option>
</select>
```

### 修改高亮颜色

#### 方法 1: 初始化时传参

```javascript
const annotator = new ArticleAnnotator('article-content', {
    highlightColor: '#e1f5fe',  // 改为浅蓝色
    selectedColor: '#81d4fa'    // 选中时的蓝色
});
```

#### 方法 2: 修改源码默认值

在 `article_annotator.js` 第 20 行左右：

```javascript
this.options = {
    highlightColor: options.highlightColor || '#e1f5fe',  // 修改默认值
    selectedColor: options.selectedColor || '#81d4fa',
    // ...
};
```

### 修改严重程度颜色

在 `article_annotator.js` 的 `getSeverityColor` 方法中（约第 250 行）：

```javascript
getSeverityColor(severity) {
    const colors = {
        low: '#4caf50',     // 绿色 - 低
        medium: '#ff9800',  // 橙色 - 中
        high: '#f44336'     // 红色 - 高
    };
    return colors[severity] || colors.medium;
}
```

### 添加新功能

#### 示例：添加批注编辑功能

1. **修改工具栏**，添加编辑模式判断
2. **添加编辑方法**：

```javascript
// 在 ArticleAnnotator 类中添加
editAnnotation(annotationId, newContent) {
    const annotation = this.annotations.find(a => a.id === annotationId);
    if (annotation) {
        annotation.content = newContent;
        annotation.updated_at = new Date().toISOString();
        
        // 通知 Streamlit
        this.notifyStreamlit({
            type: 'annotation_updated',
            annotation: annotation
        });
    }
}
```

### 性能优化建议

1. **批注数量限制**
   - 建议单篇文章批注不超过 50 个
   - 超过时考虑分页或虚拟滚动

2. **高亮渲染优化**
   - 对于大文档，考虑延迟渲染
   - 只渲染可视区域的批注

3. **数据缓存**
   - 使用 `st.cache_data` 缓存批注数据
   - 避免重复读取文件

---

## 故障排查

### 常见问题

#### 1. 工具栏不显示

**症状**：选择文本后没有弹出批注工具栏

**原因**：
- JavaScript 文件未加载
- 容器 ID 不正确
- 只读模式开启

**解决方法**：

```javascript
// 在浏览器控制台检查
console.log(window.ArticleAnnotator);  // 应该是一个函数

// 检查容器
console.log(document.getElementById('article-content'));  // 不应该是 null

// 检查初始化
console.log(annotator.options.readOnly);  // 应该是 false
```

#### 2. 批注不保存

**症状**：添加批注后刷新页面，批注消失

**原因**：
- postMessage 通信失败
- Python 端没有保存数据
- 文件路径错误

**解决方法**：

```python
# 添加调试日志
print("收到批注事件:", component_value)
print("保存路径:", file_path)

# 检查文件是否生成
import os
print("文件存在:", os.path.exists(file_path))
```

#### 3. 高亮位置错乱

**症状**：重新加载页面后，高亮位置不对

**原因**：
- 文章内容被修改
- position 数据不准确
- DOM 结构变化

**解决方法**：
- 当前版本不支持持久化高亮重现
- 只保存批注数据，不重现高亮
- 如需实现，需要更复杂的位置追踪算法

#### 4. 无法跨段落高亮

**症状**：选择跨段落的文本时无法高亮

**原因**：`range.surroundContents()` 不支持跨元素

**解决方法**：
- 这是已知限制
- 建议一次只选择单个段落内的文本
- 或使用更复杂的高亮算法（如 Rangy 库）

### 调试技巧

#### 开启浏览器控制台

```
Chrome/Edge: F12 或 Ctrl+Shift+I
Firefox: F12 或 Ctrl+Shift+K
Safari: Cmd+Option+I
```

#### 查看批注数据

```javascript
// 在控制台运行
console.log(annotator.getAnnotations());
```

#### 查看 DOM 结构

```javascript
// 查看高亮元素
console.log(document.querySelectorAll('.annotation-highlight'));
```

#### 测试通信

```javascript
// 测试 postMessage
window.parent.postMessage({
    type: 'streamlit:setComponentValue',
    value: { test: 'hello' }
}, '*');
```

### 日志记录

在 Python 端添加日志：

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 记录批注事件
logger.debug(f"批注事件: {component_value}")
logger.debug(f"保存到: {file_path}")
```

---

## 最佳实践

### 1. 批注规范

- **具体明确**：批注内容要具体，指出问题和改进方向
- **分类准确**：选择正确的批注类型
- **优先级清晰**：根据实际重要性选择严重程度

### 2. 数据管理

- **定期备份**：批注数据很重要，定期备份
- **版本控制**：考虑使用 Git 管理批注数据
- **数据清理**：定期清理无效批注

### 3. 性能考虑

- **批量操作**：避免频繁的单个保存
- **懒加载**：大文档分段加载
- **缓存优化**：使用 Streamlit 缓存机制

### 4. 团队协作

- **统一标准**：团队统一批注类型和严重程度标准
- **定期回顾**：定期回顾批注数据，优化提示词
- **知识积累**：建立模型质量知识库

---

## 未来扩展

### 短期计划

- [ ] 批注编辑功能
- [ ] 批注导出（Excel/CSV）
- [ ] 批注统计报表
- [ ] 批注搜索和筛选

### 长期计划

- [ ] 多用户协作批注
- [ ] 批注模板系统
- [ ] AI 辅助批注
- [ ] 批注质量评分

---

## 相关资源

### 文档

- [WriteArena 页面说明](../pages/13_WriteArena.py)
- [并发历史数据结构](./CONCURRENT_HISTORY_DATA_STRUCTURE.md)

### 依赖

- **Streamlit**: https://docs.streamlit.io/
- **Streamlit Components**: https://docs.streamlit.io/library/components

### 参考项目

- **Hypothesis**: https://web.hypothes.is/ (开源批注工具)
- **Annotator.js**: http://annotatorjs.org/ (JavaScript 批注库)

---

## 更新日志

### v1.0.0 (2024-10-22)

- ✅ 初始版本发布
- ✅ 基础批注功能
- ✅ 5种批注类型
- ✅ 3个严重程度
- ✅ Streamlit 集成
- ✅ 数据持久化

---

## 联系与支持

如果您在使用过程中遇到问题或有改进建议：

1. **查看文档**：先阅读本文档的故障排查部分
2. **查看代码注释**：`article_annotator.js` 有详细的代码注释
3. **添加日志**：开启调试模式查看详细信息

---

**最后更新**: 2024年10月22日  
**文档版本**: v1.0.0  
**维护状态**: 🟢 活跃维护

