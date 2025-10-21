# Auto-doc-streamlit 项目文档索引

## 📚 文档总览

本项目文档经过精心整理，按功能类型进行分类，提供了完整的使用指南和技术说明。

## 🗂️ 文档结构

### 📂 核心功能文档 (features/)
功能模块的详细说明和技术实现：

#### 主要功能
- [频道发布历史系统](./zh-CN/features/README_Channel_Publish_History.md) - 完整的频道管理和可视化平台
- [Cookie管理器](./zh-CN/features/README_cookie_manager.md) - 微信公众号登录状态管理
- [Token管理器](./zh-CN/features/README_token_manager.md) - 公众号Token自动管理

#### 数据处理
- [公众号文章自动记录](./zh-CN/features/README_gzh_auto_record.md) - 智能提取公众号文章信息
- [河流图可视化](./zh-CN/features/README_River_Flow_Visualization.md) - 专业的时间序列数据可视化
- [Web转MD工具](./zh-CN/features/README_web2md.md) - 网页内容提取和转换
- [图片处理功能](./zh-CN/features/README_web2md_images.md) - 自动下载和处理网页图片

#### 微信功能
- [微信文章处理器](./zh-CN/features/README_wechat_article_handler.md) - 处理微信文章下载和解析
- [微信自动收集器](./zh-CN/features/README_wechat_auto_collector.md) - 自动化收集微信公众号内容
- [微信下载器](./zh-CN/features/README_wechat_downloader.md) - 微信文章批量下载工具
- [微信集成功能](./zh-CN/features/README_wechat_integration.md) - 与频道发布历史的集成

### 📋 使用指南 (guides/)
操作指南、配置说明和最佳实践：

#### 数据管理
- [数据采集指南](./zh-CN/guides/DATA_COLLECTION_GUIDE.md) - 如何录入和管理频道数据
- [数据采集系统总结](./zh-CN/guides/DATA_COLLECTION_SUMMARY.md) - 数据采集系统说明和问题解答
- [删除功能指南](./zh-CN/guides/DELETE_FUNCTION_GUIDE.md) - 数据删除和管理

#### 系统配置
- [日历修复总结](./zh-CN/guides/CALENDAR_FIX_SUMMARY.md) - 日历功能的优化和修复
- [频道历史总结](./zh-CN/guides/CHANNEL_HISTORY_SUMMARY.md) - 频道发布历史系统介绍

### 📊 技术文档 (根目录)
核心技术实现和架构说明：

#### 系统架构
- [路径管理系统优化总结](./2024-08-29_PATH_Optimization_Summary.md) - 统一路径管理系统
- [频道系统V3](./CHANNEL_V3_SUMMARY.md) - 新一代频道管理系统

#### 数据处理
- [Excel处理解决方案](./EXCEL_PROCESSING_SOLUTION.md) - 完整的Excel文件处理方案
- [Excel转日历处理器](./EXCEL_TO_CALENDAR_PROCESSOR.md) - Excel数据转换和去重工具

#### 外部接口
- [今日头条账号管理](./TOUTIAO_ACCOUNT_URL_MANAGEMENT.md) - 头条号API集成
- [今日头条去重系统](./TOUTIAO_DEDUPLICATION_SYSTEM.md) - 数据去重机制

### 🔧 修复记录 (fixes/)
重要的bug修复和技术问题解决方案：
- [频道自定义块修复](./fixes/CHANNEL_CUSTOM_BLOCKS_FIX.md) - 自定义提示词块编辑功能修复
- [今日头条API重复修复](./fixes/TOUTIAO_API_DUPLICATE_FIX.md) - 重复数据问题修复

### 📈 项目总结 (summaries/)
项目开发总结和功能实现报告：

#### 最新更新
- [🆕 2025-10-21 AI转写功能重大更新](./summaries/2025-10-21_AI_Transcription_Updates.md) - 并发转写、结果对比、UI优化

#### 历史总结
- [功能总结](./summaries/FEATURE_SUMMARY.md) - 新功能实现总结
- [CSV数据迁移总结](./summaries/CSV_MIGRATION_SUMMARY.md) - 数据格式迁移报告
- [河流图可视化总结](./summaries/RIVER_FLOW_VISUALIZATION_SUMMARY.md) - 可视化功能开发总结
- [Token管理器总结](./summaries/TOKEN_MANAGER_SUMMARY.md) - Token管理系统实现总结
- [微信收集器总结](./zh-CN/summaries/WECHAT_COLLECTOR_SUMMARY.md) - 微信功能开发总结
- [项目改进建议](./summaries/2025-08-05改进建议.md) - 技术优化建议

### 📦 归档文档 (archived/)
不再活跃维护的历史文档：
- [按钮重设计](./archived/BUTTON_REDESIGN.md)
- [图标系统文档](./archived/ICONS_*.md) - 图标迁移、对比、指南、实现
- [主题使用指南](./archived/THEME_USAGE_GUIDE.md)
- [主页重设计](./archived/README_HOMEPAGE_REDESIGN.md)
- [快速开始](./archived/QUICK_START.md)
- [设计指南](./archived/DESIGN_GUIDE.md)
- [开源准备分析](./archived/开源准备分析报告.md)

## 🚀 快速开始

### 新用户入门
1. **了解项目**: 阅读 [项目主README](../README.md)
2. **数据录入**: 参考 [数据采集指南](./zh-CN/guides/DATA_COLLECTION_GUIDE.md)
3. **功能使用**: 浏览 [功能说明](./zh-CN/features/) 了解各模块

### 开发者指南
1. **系统架构**: 查看 [路径优化总结](./2024-08-29_PATH_Optimization_Summary.md)
2. **技术实现**: 阅读相应功能的技术文档
3. **修复记录**: 参考 [修复记录](./fixes/) 了解已解决的问题

## 📝 文档规范

### 命名规则
- 英文文档：`PascalCase.md` 或 `kebab-case.md`
- 中文文档：`README_功能名称.md`
- 日期文档：`YYYY-MM-DD_标题.md`

### 目录结构
```
docs/
├── README.md                    # 文档索引
├── *.md                         # 英文技术文档
├── fixes/                       # 修复记录
├── summaries/                   # 项目总结
└── zh-CN/                       # 中文文档
    ├── features/                # 功能说明
    ├── guides/                  # 使用指南
    └── summaries/               # 中文总结
```

### 维护原则
- 功能文档放在 `features/` 目录
- 使用指南放在 `guides/` 目录
- 技术实现放在根目录
- 修复记录放在 `fixes/` 目录
- 项目总结放在 `summaries/` 目录

## 🔗 相关链接

- [项目主README](../README.md) - 项目介绍和安装指南
- [项目根目录](../) - 源代码和配置文件
- [GitHub仓库](https://github.com/username/auto-doc-streamlit) - 项目仓库

---

**最后更新**: 2025年10月21日  
**文档数量**: 32个  
**维护状态**: 🟢 良好  
**最新功能**: AI并发转写、结果持久化、UI优化