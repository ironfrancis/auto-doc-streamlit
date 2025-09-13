# 微信公众号文章下载器

基于您提供的curl请求示例，我创建了一个完整的微信公众号文章下载工具。

## 🚀 功能特点

- ✅ 支持单篇文章下载
- ✅ 支持批量文章下载
- ✅ 自动生成时间戳和签名
- ✅ 保存HTML和Markdown格式
- ✅ 配置文件管理
- ✅ 交互式操作界面
- ✅ 命令行参数支持

## 📦 文件说明

### 核心文件
- `wechat_downloader.py` - 基础版本下载器
- `wechat_downloader_enhanced.py` - 增强版下载器（推荐）
- `article_urls.json` - 文章配置文件
- `README_wechat_downloader.md` - 使用说明

## 🛠️ 安装依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install requests
```

## 📖 使用方法

### 1. 基础版本

```bash
# 运行基础版本
python wechat_downloader.py

# 交互模式
python wechat_downloader.py --interactive
```

### 2. 增强版本（推荐）

```bash
# 显示帮助
python wechat_downloader_enhanced.py

# 交互模式
python wechat_downloader_enhanced.py -i

# 添加文章
python wechat_downloader_enhanced.py --add "https://mp.weixin.qq.com/s/example" --title "文章标题"

# 列出所有文章
python wechat_downloader_enhanced.py --list

# 下载所有文章
python wechat_downloader_enhanced.py --download

# 下载单篇文章
python wechat_downloader_enhanced.py --url "https://mp.weixin.qq.com/s/example"
```

## 🔧 配置文件

`article_urls.json` 文件格式：

```json
{
  "articles": [
    {
      "url": "https://mp.weixin.qq.com/s/TnXw-XNsDrsPAIuKkZPzbg",
      "title": "文章标题",
      "description": "文章描述"
    }
  ],
  "config": {
    "HTML": true,
    "MD": true,
    "delay_between_requests": 3,
    "timeout": 30
  }
}
```

## 📁 输出文件

下载的文章会保存在 `downloaded_articles/` 目录中：

- `{article_id}_{timestamp}.html` - HTML格式
- `{article_id}_{timestamp}.md` - Markdown格式
- `{article_id}_{timestamp}_response.json` - 原始响应数据

## 🎯 使用示例

### 示例1：添加并下载文章

```bash
# 添加文章
python wechat_downloader_enhanced.py --add "https://mp.weixin.qq.com/s/TnXw-XNsDrsPAIuKkZPzbg" --title "示例文章"

# 下载所有文章
python wechat_downloader_enhanced.py --download
```

### 示例2：交互模式

```bash
python wechat_downloader_enhanced.py -i
```

然后选择：
1. 添加文章
2. 移除文章
3. 列出所有文章
4. 下载单篇文章
5. 批量下载所有文章
6. 查看已下载文件
7. 退出

### 示例3：直接下载单篇文章

```bash
python wechat_downloader_enhanced.py --url "https://mp.weixin.qq.com/s/TnXw-XNsDrsPAIuKkZPzbg"
```

## ⚙️ 配置选项

### 请求配置
- `HTML`: 是否下载HTML格式（默认true）
- `MD`: 是否下载Markdown格式（默认true）
- `delay_between_requests`: 请求间隔秒数（默认3）
- `timeout`: 请求超时秒数（默认30）

### 请求头信息
脚本会自动设置以下请求头：
- `x-sign`: 自动生成的签名
- `x-timestamp`: 当前时间戳
- 其他必要的浏览器标识

## 🔍 签名算法

当前使用的签名生成算法：
```python
def generate_sign(self, timestamp):
    sign_string = f"timestamp={timestamp}&url=wechat"
    return hashlib.md5(sign_string.encode()).hexdigest()
```

如果服务器要求不同的签名算法，请修改 `generate_sign` 方法。

## ⚠️ 注意事项

1. **请求频率**: 建议在请求之间添加延迟，避免被服务器限制
2. **签名算法**: 可能需要根据实际服务器要求调整签名生成方法
3. **错误处理**: 脚本包含基本的错误处理，但可能需要根据实际情况调整
4. **文件命名**: 文件名会自动处理特殊字符，确保兼容性

## 🐛 故障排除

### 常见问题

1. **下载失败 (HTTP 403/401)**
   - 检查签名算法是否正确
   - 确认时间戳格式
   - 验证请求头信息

2. **网络连接错误**
   - 检查网络连接
   - 增加超时时间
   - 确认服务器地址正确

3. **文件保存失败**
   - 检查目录权限
   - 确认磁盘空间充足
   - 验证文件名合法性

### 调试模式

可以查看保存的 `*_response.json` 文件来了解服务器响应详情。

## 📝 更新日志

- v1.0: 基础版本，支持单篇文章下载
- v1.1: 增强版本，添加配置文件管理和批量下载
- v1.2: 添加交互模式和命令行参数支持

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和网站使用条款。 
---

**最后更新**: 2025年9月13日
