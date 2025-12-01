# 项目脚本目录

## 概述

这个目录包含了项目运行所需的核心脚本和工具，按功能分类组织。

## 📂 目录结构

```
scripts/
├── comprehensive_excel_processor.py    # 综合Excel数据处理器（主要）
├── process_excel_data.py              # Excel处理快捷脚本
├── example_river_flow_usage.py        # 河流图可视化使用示例
├── publish_excel/                     # 原始Excel数据文件
├── examples/                          # 示例脚本和演示文件
├── maintenance/                       # 维护工具脚本
├── migration/                         # 数据迁移脚本
└── workspace/                         # 工作区目录
```

## 🔧 核心脚本说明

### 1. `comprehensive_excel_processor.py`
**主要Excel数据处理脚本** - 功能最完整的Excel处理器

**功能特点：**
- 处理多种类型的文件：Excel (.xlsx/.xls)、CSV文件
- 支持多个数据源目录（原始、修复、恢复、转换的文件）
- 智能列映射和数据标准化
- 完善的去重机制和增量更新
- 多平台支持（头条号、百家号）
- 底层XML解析，处理损坏的Excel文件

**使用方法：**
```bash
python scripts/comprehensive_excel_processor.py
```

### 2. `process_excel_data.py`
**快捷使用脚本** - 调用综合处理器的简化接口

**功能特点：**
- 一键处理所有Excel文件
- 友好的用户界面和提示
- 简化的错误处理

**使用方法：**
```bash
python scripts/process_excel_data.py
```

## 文件结构

```
scripts/
├── comprehensive_excel_processor.py  # 主处理脚本（综合Excel数据处理器）
├── process_excel_data.py           # 快捷使用脚本
├── publish_excel/                  # Excel文件目录
│   ├── 头条-AGI观察室.xlsx
│   ├── 头条-漫游指南.xlsx
│   ├── 头条-看山先生.xlsx
│   ├── 头条-观察室.xlsx
│   ├── 百家号-AGI启示录.xlsx
│   └── 百家号-看山.xlsx
└── README.md                       # 本文件
```

## 输出文件

处理后的数据会保存到：
```
workspace/data/publish_history_for_calendar.csv
```

## 支持的Excel格式

- `.xlsx` 文件（推荐）
- `.xls` 文件

## 支持的列名

脚本能够自动识别以下列名变体：

| 数据类型 | 支持的列名 |
|----------|------------|
| 标题 | 标题, title, Title, 文章标题, 文章名 |
| 发布时间 | 发布时间, publish_time, PublishTime, 日期, Date |
| 阅读量 | 阅读量, read_count, ReadCount, 阅读数, 阅读, views |
| 点赞量 | 点赞量, like_count, LikeCount, 点赞数, 点赞, likes |
| 评论量 | 评论量, comment_count, CommentCount, 评论数, 评论, comments |
| 链接 | 链接, link, Link, URL, url, 文章链接 |

## 账号命名规则

- **头条号文件**: `头条-{账号名}.xlsx` → 账号名称: `头条号-{账号名}`
- **百家号文件**: `百家号-{账号名}.xlsx` → 账号名称: `百家号-{账号名}`

## 使用示例

### 基本使用
```bash
# 方法1：使用快捷脚本（推荐）
python scripts/process_excel_data.py

# 方法2：使用主处理脚本
python scripts/comprehensive_excel_processor.py
```

### 处理流程
1. 将Excel文件放入 `scripts/publish_excel/` 目录
2. 运行处理脚本
3. 检查输出结果

## 错误处理

### 常见问题

1. **Excel文件无法读取**
   - 确保文件格式正确（.xlsx 或 .xls）
   - 检查文件是否损坏
   - 尝试用Excel重新保存文件

2. **列名无法识别**
   - 检查Excel文件中的列名
   - 确保列名与支持的变体匹配

3. **数据重复**
   - 脚本会自动去重
   - 检查Excel文件本身是否有重复数据

## 日志输出

脚本会输出详细的处理日志：

```
🚀 Excel数据处理工具
==================================================
📁 处理目录: scripts/publish_excel/
📄 输出文件: workspace/data/publish_history_for_calendar.csv
==================================================
📁 找到 6 个Excel文件
📖 正在处理文件: /path/to/file.xlsx
📊 原始数据: 10 行
✅ 处理后数据: 10 行
📚 现有数据: 177 条
➕ 发现 11 条新记录
🔄 发现 0 条需要更新的记录
🔗 合并后共 188 条记录
💾 数据已保存到 /path/to/file.csv，共 188 条记录
🎉 所有Excel文件处理完成！
✅ 处理完成！
```

## 注意事项

1. **文件权限**: 确保脚本有读取Excel文件和写入CSV文件的权限
2. **数据备份**: 建议在处理前备份重要的CSV文件
3. **定期运行**: 建议定期运行脚本以保持数据同步
4. **文件格式**: 推荐使用 `.xlsx` 格式的Excel文件

## 技术细节

- **Python版本**: 3.6+
- **依赖库**: pandas, openpyxl, xlrd
- **编码**: UTF-8
- **去重机制**: 基于标题+发布时间+账号名称+链接的组合

## 更新日志

- **v1.0**: 初始版本，支持基本的Excel处理
- **v1.1**: 添加多引擎支持，改进错误处理
- **v1.2**: 优化去重逻辑，添加增量更新功能
- **v1.3**: 添加快捷使用脚本，改进用户体验
