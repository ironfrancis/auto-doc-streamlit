# 微信公众号文章自动收集器

## 功能概述

这个工具专门用于处理微信公众号文章，包括：

1. **自动检测环境异常** - 当页面显示"环境异常"时，自动使用Selenium处理
2. **智能下载** - 支持多种下载方式，包括API下载和Selenium抓取
3. **自动记录** - 自动保存文章信息和下载记录
4. **批量处理** - 支持批量处理多篇文章
5. **数据统计** - 提供详细的下载统计信息

## 安装依赖

```bash
pip install requests selenium pandas
```

## 使用方法

### 1. 检查页面状态

```bash
python wechat_article_handler.py --check "https://mp.weixin.qq.com/s/YEEgiKCu2YMUls7QFJ24EQ"
```

### 2. 处理单篇文章

```bash
python wechat_article_handler.py --url "https://mp.weixin.qq.com/s/YEEgiKCu2YMUls7QFJ24EQ" --channel "科技频道" --title "文章标题"
```

### 3. 添加文章到队列

```bash
python wechat_article_handler.py --add-article "https://mp.weixin.qq.com/s/YEEgiKCu2YMUls7QFJ24EQ" --channel "科技频道" --title "文章标题"
```

### 4. 批量处理

```bash
python wechat_article_handler.py --batch
```

### 5. 查看记录

```bash
python wechat_article_handler.py --list
```

### 6. 查看统计信息

```bash
python wechat_article_handler.py --stats
```

## 处理环境异常

当遇到"环境异常"页面时，工具会：

1. 自动检测异常状态
2. 启动Selenium浏览器
3. 尝试自动点击验证按钮
4. 提取页面内容
5. 保存文章信息

## 文件结构

```
├── wechat_article_handler.py          # 主程序
├── wechat_handler_config.json         # 配置文件
├── workspace/data/wechat_records/     # 记录目录
│   └── wechat_article_records.json   # 记录文件
├── downloaded_articles/               # 下载目录
│   ├── *.html                        # HTML文件
│   ├── *.md                          # Markdown文件
│   └── *_response.json               # 响应数据
└── README_wechat_article_handler.md  # 说明文档
```

## 配置选项

在 `wechat_handler_config.json` 中可以配置：

```json
{
  "articles": [],
  "channels": [],
  "settings": {
    "HTML": true,
    "MD": true,
    "delay_between_requests": 3,
    "timeout": 30,
    "auto_record": true,
    "save_content": true,
    "use_selenium": true,
    "selenium_timeout": 10
  }
}
```

## 记录格式

每篇文章的记录包含：

```json
{
  "id": "wechat_0001",
  "url": "https://mp.weixin.qq.com/s/...",
  "title": "文章标题",
  "channel_name": "频道名称",
  "download_time": "2024-01-01T12:00:00",
  "status": "success",
  "content_files": ["path/to/file.html"],
  "metadata": {
    "author": "作者",
    "publish_time": "发布时间",
    "word_count": 1000,
    "read_count": 0,
    "like_count": 0
  }
}
```

## 处理流程

1. **检查页面状态** - 检测是否出现环境异常
2. **选择处理方式** - 根据状态选择API下载或Selenium处理
3. **下载内容** - 获取文章HTML和Markdown内容
4. **保存文件** - 保存到本地目录
5. **记录信息** - 自动记录下载信息
6. **更新统计** - 更新下载统计

## 注意事项

1. **Selenium依赖** - 需要安装Chrome浏览器和ChromeDriver
2. **网络环境** - 某些网络环境可能需要代理
3. **验证码** - 复杂的验证码可能需要手动处理
4. **频率限制** - 建议设置适当的延迟避免被封

## 故障排除

### 1. Selenium初始化失败
- 检查Chrome浏览器是否安装
- 检查ChromeDriver是否在PATH中
- 尝试更新ChromeDriver版本

### 2. 环境异常无法处理
- 检查网络连接
- 尝试手动访问页面
- 可能需要更换IP或使用代理

### 3. 下载失败
- 检查API服务是否正常
- 检查网络连接
- 查看错误日志

## 示例脚本

### 批量处理示例

```python
from wechat_article_handler import WeChatArticleHandler

handler = WeChatArticleHandler()

# 添加文章
handler.add_article("https://mp.weixin.qq.com/s/...", "科技频道", "文章标题")

# 批量处理
handler.batch_process()

# 查看统计
handler.get_statistics()
```

### 自定义处理

```python
# 检查页面状态
status = handler.check_page_status("https://mp.weixin.qq.com/s/...")
print(f"状态: {status['status']}")

# 处理环境异常
if status['status'] == "environment_error":
    result = handler.handle_environment_error("https://mp.weixin.qq.com/s/...")
    print(f"处理结果: {result['status']}")
```

## 更新日志

- v1.0.0: 初始版本，支持基本下载和记录功能
- v1.1.0: 添加Selenium支持，处理环境异常
- v1.2.0: 优化错误处理和统计功能 