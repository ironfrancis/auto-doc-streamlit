# 53AI网站文章爬虫使用说明

## 功能概述

`source_53ai.py` 是一个专门用于爬取53AI网站文章信息的Python爬虫工具。它能够自动获取53AI网站上的所有文章，包括标题、URL、发布时间、内容等信息。

## 主要特性

- **自动爬取**: 支持多页爬取，自动识别文章列表
- **内容提取**: 智能提取文章正文内容
- **数据清洗**: 自动清理HTML标签，提取纯文本内容
- **CSV导出**: 将爬取结果保存为CSV格式文件
- **错误处理**: 完善的异常处理和重试机制

## 使用方法

### 1. 基本使用

```python
from app.utils.source_53ai import Source53AI

# 创建爬虫实例
crawler = Source53AI()

# 爬取文章（默认5页）
df = crawler.crawl_articles(5)

# 保存到CSV
filename = crawler.save_to_csv(df)
```

### 2. 自定义爬取

```python
# 爬取指定页数
df = crawler.crawl_articles(max_pages=10)

# 获取单个页面
html_content = crawler.get_news_page(page=1)

# 解析文章列表
articles = crawler.parse_articles(html_content)

# 获取文章详情
content = crawler.get_article_content(article_url)
```

### 3. 直接运行

```bash
cd app/utils
python source_53ai.py
```

## 输出数据格式

爬取的数据包含以下字段：

| 字段名 | 说明 | 示例 |
|--------|------|------|
| title | 文章标题 | "大模型技术" |
| url | 文章链接 | "https://www.53ai.com/news/LargeLanguageModel" |
| publish_time | 发布时间 | "2025-08-22 13:35:33" |
| source | 数据来源 | "53AI" |
| platform | 平台类型 | "website" |
| content | 文章内容 | "大模型技术 - 53AI-AI知识库..." |

## 技术实现

### 1. 页面获取
- 使用 `requests` 库发送HTTP请求
- 设置合理的User-Agent避免被反爬
- 支持超时和重试机制

### 2. 内容解析
- 使用正则表达式提取文章链接和标题
- 支持多种HTML结构模式
- 备用BeautifulSoup解析方案

### 3. 内容提取
- 多种内容提取模式
- 自动清理HTML标签
- 文本长度和质量控制

### 4. 数据存储
- 使用pandas DataFrame管理数据
- CSV格式导出，支持中文编码
- 自动生成带时间戳的文件名

## 注意事项

### 1. 爬取频率
- 内置0.5秒延迟，避免请求过快
- 建议不要频繁运行，避免对目标网站造成压力

### 2. 内容质量
- 提取的内容可能包含导航菜单等无关信息
- 建议根据实际需求进行内容过滤和清洗

### 3. 网站结构变化
- 如果网站结构发生变化，可能需要更新正则表达式
- 建议定期检查爬虫是否正常工作

## 扩展功能

### 1. 添加更多数据源
```python
class Source53AI:
    def __init__(self):
        # 可以添加更多网站URL
        self.other_urls = [
            "https://other-ai-site.com",
            "https://another-ai-blog.com"
        ]
```

### 2. 自定义内容过滤
```python
def filter_content(self, content):
    """自定义内容过滤逻辑"""
    # 移除特定关键词
    # 保留特定段落
    # 格式化文本
    return processed_content
```

### 3. 数据库存储
```python
def save_to_database(self, df):
    """保存到数据库"""
    # 连接数据库
    # 插入数据
    # 处理重复数据
```

## 故障排除

### 1. 网络连接问题
- 检查网络连接
- 确认目标网站可访问
- 检查防火墙设置

### 2. 内容提取失败
- 检查网站HTML结构是否变化
- 更新正则表达式模式
- 尝试使用BeautifulSoup备用方案

### 3. 编码问题
- 确认网页编码设置
- 检查CSV文件编码
- 使用UTF-8编码保存

## 更新日志

- **v1.0**: 基础爬虫功能
- **v1.1**: 改进内容提取逻辑
- **v1.2**: 添加BeautifulSoup备用解析
- **v1.3**: 优化错误处理和重试机制

## 许可证

本项目仅供学习和研究使用，请遵守相关网站的使用条款和robots.txt规定。
