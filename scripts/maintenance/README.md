# 🛠️ 维护工具脚本目录

本目录包含项目维护和开发过程中使用的各种工具脚本。

## 📂 当前目录结构

```
maintenance/
├── clear_sample_data.py      # 清空示例数据工具
├── list_files.py             # 文件列表查看工具
├── view_pdf_images.py        # PDF图片查看器
├── workspace_config.py       # 工作区配置文件
└── README.md                # 本说明文件
```

## 🔧 工具说明

### 数据管理工具
- **clear_sample_data.py**: 清空示例数据，备份现有数据到JSON文件
- **list_files.py**: 列出项目中的所有文件，支持排除特定目录

### 文件处理工具
- **view_pdf_images.py**: Streamlit应用，用于查看PDF文件中的图片内容

### 配置工具
- **workspace_config.py**: 定义工作区目录路径的配置文件

## 🚀 使用方法

### 命令行运行
```bash
# 清空示例数据
python scripts/maintenance/clear_sample_data.py

# 查看PDF图片
python scripts/maintenance/view_pdf_images.py

# 列出项目文件
python scripts/maintenance/list_files.py
```

### 作为模块导入
```python
from scripts.maintenance.workspace_config import get_workspace_path
from scripts.maintenance.clear_sample_data import backup_current_data
```

## 📝 注意事项

- 工具脚本主要用于开发和维护阶段
- 生产环境建议通过Streamlit界面使用相应的功能
- 新增工具脚本请更新此README文档 