# 微信公众号自动收集器使用指南

## 概述

我为您创建了一套完整的微信公众号文章自动收集和记录系统，包含以下工具：

1. **`simple_wechat_collector.py`** - 简化版收集器，适合单次处理
2. **`auto_wechat_monitor.py`** - 自动监控器，支持定期检查和记录
3. **`wechat_article_handler.py`** - 增强版处理器，支持Selenium处理环境异常

## 功能特点

### ✅ 已实现功能

1. **自动检测环境异常** - 当页面显示"环境异常"时自动识别
2. **智能内容提取** - 自动提取文章标题、作者、发布时间、正文内容
3. **多格式保存** - 支持HTML和纯文本格式保存
4. **自动记录** - 自动记录下载信息和统计
5. **批量处理** - 支持批量处理多篇文章
6. **定期监控** - 支持定时检查和自动记录
7. **详细日志** - 完整的操作日志记录

### 📊 数据记录

每篇文章会自动记录以下信息：
- 文章ID、URL、标题、频道
- 下载时间、状态、HTTP状态码
- 作者、发布时间、字数统计
- 内容摘要、文件路径
- 下载统计信息

## 快速开始

### 1. 安装依赖

```bash
pip install requests pandas schedule
```

### 2. 单次处理文章

```bash
# 处理单篇文章
python simple_wechat_collector.py --url "https://mp.weixin.qq.com/s/YEEgiKCu2YMUls7QFJ24EQ" --channel "AGI观察室" --title "职场AI新范式"

# 检查页面状态
python simple_wechat_collector.py --check "https://mp.weixin.qq.com/s/YEEgiKCu2YMUls7QFJ24EQ"
```

### 3. 自动监控

```bash
# 添加监控项目
python auto_wechat_monitor.py --add "https://mp.weixin.qq.com/s/YEEgiKCu2YMUls7QFJ24EQ" --channel "AGI观察室" --title "职场AI新范式"

# 立即检查所有项目
python auto_wechat_monitor.py --check

# 查看监控状态
python auto_wechat_monitor.py --status

# 启动自动监控（每小时检查一次）
python auto_wechat_monitor.py --start
```

## 文件结构

```
├── simple_wechat_collector.py      # 简化版收集器
├── auto_wechat_monitor.py          # 自动监控器
├── wechat_article_handler.py       # 增强版处理器
├── simple_wechat_config.json       # 简化版配置
├── auto_monitor_config.json        # 监控配置
├── wechat_articles/                # 下载的文章
│   ├── *.html                      # HTML文件
│   └── *.txt                       # 文本文件
├── workspace/data/wechat_records/  # 记录文件
│   ├── wechat_article_records.json # 文章记录
│   └── monitor_status.json         # 监控状态
└── wechat_monitor.log              # 操作日志
```

## 配置说明

### 监控配置 (auto_monitor_config.json)

```json
{
  "monitor_settings": {
    "check_interval": 3600,        // 检查间隔（秒）
    "auto_download": true,         // 自动下载
    "save_content": true,          // 保存内容
    "timeout": 30,                 // 超时时间
    "delay_between_requests": 3    // 请求间隔
  },
  "watch_list": [
    {
      "url": "https://mp.weixin.qq.com/s/...",
      "channel": "AGI观察室",
      "title": "文章标题",
      "description": "描述",
      "last_check": null,
      "status": "pending"
    }
  ]
}
```

## 使用示例

### 示例1：处理您提到的文章

```bash
# 检查文章状态
python simple_wechat_collector.py --check "https://mp.weixin.qq.com/s/YEEgiKCu2YMUls7QFJ24EQ"

# 处理并记录文章
python simple_wechat_collector.py --url "https://mp.weixin.qq.com/s/YEEgiKCu2YMUls7QFJ24EQ" --channel "AGI观察室" --title "职场AI新范式：超级麦吉Vibe Working"
```

### 示例2：设置自动监控

```bash
# 添加监控项目
python auto_wechat_monitor.py --add "https://mp.weixin.qq.com/s/YEEgiKCu2YMUls7QFJ24EQ" --channel "AGI观察室" --title "职场AI新范式"

# 启动自动监控
python auto_wechat_monitor.py --start
```

### 示例3：查看记录和统计

```bash
# 查看最近记录
python simple_wechat_collector.py --list

# 查看统计信息
python simple_wechat_collector.py --stats

# 查看监控状态
python auto_wechat_monitor.py --status
```

## 处理环境异常

当遇到"环境异常"页面时，系统会：

1. **自动检测** - 识别环境异常状态
2. **记录信息** - 保存异常状态和页面内容
3. **统计记录** - 更新失败统计
4. **日志记录** - 详细记录处理过程

## 数据导出

### 查看记录

```bash
# 列出最近10条记录
python simple_wechat_collector.py --list

# 查看统计信息
python simple_wechat_collector.py --stats
```

### 导出数据

记录文件位置：
- `workspace/data/wechat_records/wechat_article_records.json` - 文章记录
- `workspace/data/wechat_records/monitor_status.json` - 监控状态
- `wechat_monitor.log` - 操作日志

## 故障排除

### 常见问题

1. **环境异常无法处理**
   - 检查网络连接
   - 尝试手动访问页面
   - 可能需要更换IP或使用代理

2. **下载失败**
   - 检查URL是否正确
   - 检查网络连接
   - 查看错误日志

3. **监控停止**
   - 检查配置文件
   - 查看日志文件
   - 重新启动监控

### 日志查看

```bash
# 查看操作日志
tail -f wechat_monitor.log

# 查看错误信息
grep "ERROR" wechat_monitor.log
```

## 高级功能

### 批量处理

```bash
# 添加多个文章到队列
python simple_wechat_collector.py --add-article "URL1" --channel "频道1" --title "标题1"
python simple_wechat_collector.py --add-article "URL2" --channel "频道2" --title "标题2"

# 批量处理
python simple_wechat_collector.py --batch
```

### 自定义配置

可以修改配置文件来自定义：
- 检查间隔时间
- 保存内容格式
- 请求延迟时间
- 超时设置

## 安全注意事项

1. **频率限制** - 建议设置适当的延迟避免被封
2. **网络环境** - 某些网络环境可能需要代理
3. **验证码** - 复杂的验证码可能需要手动处理
4. **数据备份** - 定期备份记录文件

## 更新日志

- **v1.0.0** - 基础功能，支持单次处理和记录
- **v1.1.0** - 添加自动监控和定时检查
- **v1.2.0** - 优化错误处理和日志记录
- **v1.3.0** - 添加环境异常检测和统计功能

## 技术支持

如果您在使用过程中遇到问题，可以：

1. 查看日志文件 `wechat_monitor.log`
2. 检查配置文件是否正确
3. 确认网络连接正常
4. 查看错误信息和状态码

---

**注意**：本工具仅用于学习和研究目的，请遵守相关网站的使用条款和法律法规。 