# 今日头条账号URL管理系统

## 概述

这个系统实现了基于账号ID的智能URL管理，可以根据不同账号的Cookie自动选择对应的API请求URL。

## 核心功能

### 1. 账号ID自动提取
- 从Cookie字符串中智能提取账号ID
- 支持多种Cookie字段：`uid_tt`、`toutiao_sso_user`、`tt_webid`、`sessionid`
- 自动清理Cookie中的换行符和空格

### 2. URL映射管理
- 维护账号ID到专用URL的映射字典
- 支持为不同账号配置不同的API参数
- 自动为新账号生成默认URL模板

### 3. 智能URL选择
- 根据提取的账号ID自动选择对应的URL
- 如果账号未配置，使用默认URL模板
- 支持动态添加新账号的URL配置

## 使用方法

### 基本使用

```python
from core.crawlers.toutiao_api import fetch_article_by_site, update_toutiao_publish_history

# 使用Cookie获取数据
cookie_str = "你的Cookie字符串"
df = fetch_article_by_site(cookie_str)
update_toutiao_publish_history(cookie_str)
```

### 管理账号URL

```python
from core.crawlers.toutiao_api import add_account_url, list_account_urls, get_url_for_account

# 添加新账号的URL
add_account_url("账号ID", "自定义URL")

# 列出所有已配置的账号
list_account_urls()

# 获取特定账号的URL
url = get_url_for_account("账号ID")
```

## 配置账号URL

### 方法1：在代码中直接配置

```python
# 在 url_dict 中添加新账号
url_dict = {
    "账号ID1": "对应的完整URL",
    "账号ID2": "对应的完整URL",
    # ...
}
```

### 方法2：动态添加

```python
# 为账号添加默认URL模板
add_account_url("新账号ID")

# 为账号添加自定义URL
add_account_url("新账号ID", "https://mp.toutiao.com/api/...")
```

## 账号ID提取规则

系统会按以下顺序尝试提取账号ID：

1. `uid_tt=账号ID`
2. `toutiao_sso_user=账号ID`
3. `tt_webid=数字ID`
4. `sessionid=账号ID`

## URL模板说明

默认URL模板包含以下参数：
- `visited_uid`: 账号ID（动态替换）
- `count`: 获取数量（默认100）
- `category`: 内容分类
- `client_extra_params`: 客户端额外参数

## 错误处理

- **Cookie无效**: 自动检测并提示重新登录
- **账号未配置**: 使用默认URL模板
- **网络错误**: 提供详细的错误信息
- **数据格式错误**: 优雅处理并继续执行

## 扩展性

### 添加新账号类型
1. 在 `extract_account_id_from_cookie` 函数中添加新的正则表达式模式
2. 在 `url_dict` 中添加对应的URL配置
3. 根据需要调整URL模板参数

### 自定义URL参数
每个账号可以有不同的：
- 获取数量限制
- 内容分类筛选
- 时间范围限制
- 其他API参数

## 示例

### 完整使用流程

```python
# 1. 提取账号ID
account_id = extract_account_id_from_cookie(cookie_str)
print(f"账号ID: {account_id}")

# 2. 检查是否需要添加URL配置
if account_id not in url_dict:
    add_account_url(account_id)

# 3. 获取数据
df = fetch_article_by_site(cookie_str)

# 4. 保存数据
update_toutiao_publish_history(cookie_str)
```

### 批量管理多个账号

```python
# 配置多个账号
accounts = {
    "账号1": "URL1",
    "账号2": "URL2",
    "账号3": "URL3"
}

for account_id, url in accounts.items():
    add_account_url(account_id, url)

# 列出所有配置
list_account_urls()
```

## 注意事项

1. **Cookie有效性**: 确保Cookie未过期且有效
2. **账号权限**: 确保账号有访问API的权限
3. **请求频率**: 避免过于频繁的请求
4. **URL参数**: 不同账号可能需要不同的参数配置

## 故障排除

### 常见问题

1. **HTTP 400错误**: 检查URL参数是否正确
2. **账号ID提取失败**: 检查Cookie格式是否正确
3. **数据获取为空**: 检查账号是否有发布内容
4. **权限不足**: 检查Cookie是否有效

### 调试方法

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查账号ID提取
account_id = extract_account_id_from_cookie(cookie_str)
print(f"提取的账号ID: {account_id}")

# 检查URL选择
url = get_url_for_account(account_id)
print(f"选择的URL: {url}")
```

---

**最后更新**: 2025年9月13日
