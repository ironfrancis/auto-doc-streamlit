# Web to MD 图片下载功能说明

## 功能概述

在 `3_Web_to_MD.py` 页面中，新增了图片自动下载功能。当从网页提取Markdown内容时，可以选择同时下载网页中的图片到本地。

## 使用方法

### 1. 启用图片下载
在Web to MD页面中，勾选 "Download Images to Local" 选项：
- ✅ **启用**：自动下载网页中的图片到本地
- ❌ **禁用**：不下载图片，保持原始链接

### 2. 图片处理流程
1. **网页内容提取**：使用MagicLens提取网页内容为Markdown
2. **图片识别**：识别Markdown内容中的图片链接
3. **图片下载**：自动下载网络图片到本地目录
4. **路径更新**：更新Markdown中的图片路径为绝对路径
5. **文件保存**：保存处理后的Markdown文件

### 3. 图片保存位置
- **目录**：`workspace/images/processed/`
- **命名规则**：`web_img_{timestamp}_{hash}.{ext}`
- **示例**：`web_img_1703123456_a1b2c3d4.jpg`

## 支持的图片类型

### 网络图片
- HTTP/HTTPS链接
- 相对路径（自动转换为绝对路径）
- 各种图片格式：PNG、JPG、JPEG、GIF、WebP

### 图片格式检测
- 优先从HTTP响应头获取Content-Type
- 从URL路径获取文件扩展名
- 默认使用.jpg格式

## 错误处理

### 下载失败的情况
- 网络连接问题
- 图片URL无效
- 服务器返回错误
- 文件权限问题

### 处理方式
- 保持原始图片链接
- 在Markdown中添加注释说明下载失败
- 继续处理其他图片

## 使用示例

### 输入网页
```
https://example.com/article-with-images
```

### 提取的Markdown内容
```markdown
# 文章标题

这是一篇包含图片的文章。

![图片1](https://example.com/image1.jpg)
![图片2](https://example.com/image2.png)
```

### 处理后的Markdown内容
```markdown
# 文章标题

这是一篇包含图片的文章。

![图片1](/Users/username/Projects/Auto-doc-streamlit/workspace/images/processed/web_img_1703123456_a1b2c3d4.jpg)
![图片2](/Users/username/Projects/Auto-doc-streamlit/workspace/images/processed/web_img_1703123457_e5f6g7h8.png)
```

## 注意事项

1. **网络连接**：需要稳定的网络连接来下载图片
2. **存储空间**：图片会占用本地存储空间
3. **处理时间**：图片下载会增加处理时间
4. **文件权限**：确保对 `workspace/images/processed/` 目录有写权限
5. **重复下载**：相同URL的图片会生成不同的文件名

## 技术实现

### 核心函数
- `download_image()`: 下载单个图片
- `process_images_in_markdown()`: 处理Markdown中的图片
- `extract_markdown_from_url()`: 主提取函数（新增图片处理参数）

### 依赖库
- `requests`: 网络请求
- `hashlib`: 生成文件名哈希
- `urllib.parse`: URL处理
- `re`: 正则表达式匹配

## 故障排除

### 常见问题
1. **图片下载失败**
   - 检查网络连接
   - 验证图片URL是否可访问
   - 查看控制台错误信息

2. **文件权限错误**
   - 确保 `workspace/images/processed/` 目录存在
   - 检查目录写权限

3. **处理时间过长**
   - 减少图片数量
   - 检查网络速度
   - 考虑禁用图片下载

### 调试信息
在控制台中会显示：
- 图片下载进度
- 成功/失败的图片数量
- 错误详情 
---

**最后更新**: 2025年9月13日
