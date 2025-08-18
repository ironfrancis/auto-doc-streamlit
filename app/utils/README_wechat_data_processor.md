# 微信公众号数据处理工具

## 功能概述

`wechat_data_processor.py` 是一个统一的微信公众号数据处理工具，集成了以下功能：

1. **Excel文件处理** - 处理微信公众号导出的Excel数据文件
2. **URL信息获取** - 从微信公众号文章URL获取发布信息
3. **批量URL处理** - 批量处理多个文章URL
4. **数据合并** - 自动合并新旧数据并去重

## 主要功能

### 1. Excel文件处理 (`process_excel_file`)

处理微信公众号导出的Excel文件，自动合并到CSV数据文件中。

```python
from wechat_data_processor import process_excel_file

# 处理Excel文件
success = process_excel_file("path/to/excel_file.xls")
if success:
    print("处理成功")
```

### 2. URL信息获取 (`get_gzh_publish_info`)

从微信公众号文章URL获取发布信息，包括标题、发布时间、公众号名称等。

```python
from wechat_data_processor import get_gzh_publish_info

# 获取文章信息
info = get_gzh_publish_info("https://mp.weixin.qq.com/s/xxx")
print(f"标题: {info['title']}")
print(f"发布时间: {info['create_time']}")
print(f"公众号: {info['nickname']}")
```

### 3. 批量URL处理 (`process_url_list`)

批量处理多个微信公众号文章URL，自动获取信息并保存到CSV。

```python
from wechat_data_processor import process_url_list

# 批量处理URL列表
urls = [
    "https://mp.weixin.qq.com/s/url1",
    "https://mp.weixin.qq.com/s/url2",
    "https://mp.weixin.qq.com/s/url3"
]
success = process_url_list(urls)
```

## 命令行使用

### 1. 处理Excel文件

```bash
python wechat_data_processor.py excel path/to/excel_file.xls
```

### 2. 批量处理URL列表

```bash
python wechat_data_processor.py urls "https://mp.weixin.qq.com/s/url1" "https://mp.weixin.qq.com/s/url2"
```

### 3. 获取单个URL信息

```bash
python wechat_data_processor.py url "https://mp.weixin.qq.com/s/xxx"
```

## 数据格式

### 输入Excel格式

支持微信公众号导出的Excel文件，包含以下列：
- 内容标题
- 发表时间
- 总阅读人数
- 总分享人数
- 内容url
- 等...

### 输出CSV格式

统一输出到 `workspace/data/publish_history.csv`，包含以下字段：

| 字段名 | 说明 |
|--------|------|
| 内容标题 | 文章标题 |
| 发表时间 | 发布时间（YYYYMMDD格式） |
| 总阅读人数 | 阅读人数 |
| 总分享人数 | 分享人数 |
| 内容url | 文章链接 |
| channel_name | 频道/公众号名称 |
| publish_date | 发布日期（YYYY-MM-DD格式） |
| publish_time | 发布时间 |
| status | 状态（published/draft/scheduled） |
| likes | 点赞数 |
| comments | 评论数 |
| id | 记录ID |
| tags | 标签 |

## 依赖包

工具会自动检查并安装以下依赖：
- `pandas` - 数据处理
- `openpyxl` - Excel文件读取
- `tabulate` - 数据展示
- `requests` - HTTP请求

## 错误处理

- 自动检查依赖包并尝试安装
- 文件不存在时给出明确错误信息
- 网络请求超时处理
- 数据格式错误处理
- 详细的错误日志输出

## 使用示例

### 示例1：处理Excel文件

```python
from wechat_data_processor import process_excel_file

# 处理Excel文件
success = process_excel_file("app/utils/agi观察室7月份.xls")
if success:
    print("Excel文件处理完成，数据已保存到CSV")
```

### 示例2：获取文章信息

```python
from wechat_data_processor import get_gzh_publish_info

# 获取文章信息
url = "https://mp.weixin.qq.com/s/xxx"
info = get_gzh_publish_info(url)
print(f"文章标题: {info['title']}")
print(f"发布时间: {info['create_time']}")
print(f"公众号: {info['nickname']}")
```

### 示例3：批量处理URL

```python
from wechat_data_processor import process_url_list

# 批量处理URL
urls = [
    "https://mp.weixin.qq.com/s/article1",
    "https://mp.weixin.qq.com/s/article2"
]
success = process_url_list(urls)
if success:
    print("批量处理完成")
```

## 注意事项

1. **网络连接** - URL信息获取需要网络连接
2. **文件权限** - 确保有读写CSV文件的权限
3. **数据备份** - 建议在处理前备份现有数据
4. **URL格式** - 确保URL是有效的微信公众号文章链接
5. **数据去重** - 工具会自动根据URL去重，避免重复数据

## 更新日志

- v1.0.0 - 初始版本，集成Excel处理和URL信息获取功能
- 支持批量URL处理
- 自动依赖检查和安装
- 完善的错误处理机制 