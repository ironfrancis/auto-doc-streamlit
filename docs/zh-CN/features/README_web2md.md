# Web2MD - 网页内容提取工具

这个工具使用MagicLens.js脚本从网页提取内容并转换为Markdown格式。它能够智能分析网页结构，提取主要内容，并保留格式。

## 功能特点

- 支持两种提取模式：
  - `viewport`: 只提取视口内可见的内容（默认）
  - `all`: 提取页面上所有内容
- 自动处理标题、段落、列表、链接、图片等HTML元素
- 智能过滤广告、导航栏、页脚等无关内容
- 自动保存到项目的`workspace/articles/ori_docs`目录

## 安装依赖

在使用此工具前，请确保安装了所需的Python依赖：

```bash
pip install selenium webdriver-manager
```

## 命令行使用方法

```bash
python app/web2md.py [URL] [选项]
```

### 参数说明

- `URL`: 要提取内容的网页地址
- `-o, --output`: 输出文件路径（可选，默认保存到workspace/articles/ori_docs目录）
- `-s, --scope`: 提取范围，可选`all`或`viewport`（默认为`viewport`）
- `-w, --wait`: 等待页面加载的时间（秒）（默认为5秒）

### 示例

```bash
# 使用默认设置提取网页内容
python app/web2md.py https://example.com

# 提取所有内容并指定输出文件
python app/web2md.py https://example.com -s all -o output.md

# 增加页面加载等待时间（对于复杂页面）
python app/web2md.py https://example.com -w 10
```

## 在代码中使用

您也可以在Python代码中导入并使用此功能：

```python
from app.web2md import extract_markdown_from_url

# 提取网页内容
markdown = extract_markdown_from_url(
    url="https://example.com",
    output_file="output.md",  # 可选
    scope="viewport",         # 可选，默认为"viewport"
    wait_time=5               # 可选，默认为5秒
)

# 处理提取的Markdown内容
print(markdown)
```

## 注意事项

1. 此工具需要Chrome浏览器
2. 对于动态加载的内容，可能需要增加等待时间
3. 某些网站可能有反爬虫措施，可能影响提取效果
4. 提取结果的质量取决于网页的结构和MagicLens的分析能力

---

**最后更新**: 2025年9月13日
