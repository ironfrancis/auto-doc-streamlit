# 🛠️ 工具脚本目录

本目录包含项目开发过程中使用的各种工具脚本，按功能分类存放。

## 📂 目录结构

```
tools/
├── image_processing/     # 图片处理工具
│   ├── download_pdf_images.py      # PDF图片下载器
│   ├── view_pdf_images.py         # PDF图片查看器
│   ├── image_search_demo.py       # 图片搜索演示
│   └── powerfulscreenshot.py      # 网页截图工具
├── demo/                 # 演示脚本
│   └── demo_channel_history.py   # 频道历史演示
├── utils/                # 通用工具
│   ├── clear_sample_data.py      # 清空示例数据
│   └── list_files.py             # 文件列表工具
└── README.md            # 本说明文件
```

## 🔧 工具说明

### 图片处理工具 (image_processing/)
- **download_pdf_images.py**: 从PDF文件中提取和下载图片
- **view_pdf_images.py**: 查看PDF文件中的图片内容
- **image_search_demo.py**: 演示图片搜索功能
- **powerfulscreenshot.py**: 网页截图和保存工具

### 演示脚本 (demo/)
- **demo_channel_history.py**: 频道发布历史记录功能演示

### 通用工具 (utils/)
- **clear_sample_data.py**: 清空示例数据，备份现有数据
- **list_files.py**: 列出项目中的所有文件

## 🚀 使用方法

这些工具脚本可以通过以下方式使用：

1. **在Streamlit应用中**: 通过主应用的"工具"菜单访问
2. **命令行直接运行**: 在项目根目录下运行
3. **作为模块导入**: 在其他Python脚本中导入使用

## 📝 注意事项

- 所有工具脚本都保持独立，不依赖特定的运行环境
- 工具脚本主要用于开发和维护，生产环境建议通过Streamlit界面使用
- 新增工具脚本请按功能分类放入对应目录 