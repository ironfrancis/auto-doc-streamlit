#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径管理器
统一管理所有数据路径，支持workspace和legacy路径
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

try:
    from workspace_config import WORKSPACE_DIRS, get_workspace_path
    WORKSPACE_AVAILABLE = True
except ImportError:
    WORKSPACE_AVAILABLE = False

class PathManager:
    """路径管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.workspace_available = WORKSPACE_AVAILABLE
        
    def get_md_review_dir(self):
        """获取MD审核目录"""
        if self.workspace_available:
            return get_workspace_path("articles", "md_review")
        else:
            return self.project_root / "app" / "md_review"
    
    def get_static_dir(self):
        """获取静态文件目录"""
        if self.workspace_available:
            return get_workspace_path("data", "html")
        else:
            return self.project_root / "app" / "static"
    
    def get_images_dir(self):
        """获取图片目录"""
        if self.workspace_available:
            return get_workspace_path("images", "processed")
        else:
            return self.project_root / "app" / "static" / "images"
    
    def get_ori_docs_dir(self):
        """获取原始文档目录"""
        if self.workspace_available:
            return get_workspace_path("articles", "ori_docs")
        else:
            return self.project_root / "ori_docs"
    
    def get_wechat_articles_dir(self):
        """获取微信文章目录"""
        if self.workspace_available:
            return get_workspace_path("articles", "wechat_articles")
        else:
            return self.project_root / "wechat_articles"
    
    def get_downloaded_images_dir(self):
        """获取下载图片目录"""
        if self.workspace_available:
            return get_workspace_path("images", "downloaded")
        else:
            return self.project_root / "downloaded_images"
    
    def get_json_data_dir(self):
        """获取JSON数据目录"""
        if self.workspace_available:
            return get_workspace_path("data", "json")
        else:
            return self.project_root / "app"
    
    def get_generated_dir(self):
        """获取生成内容目录"""
        if self.workspace_available:
            return get_workspace_path("articles", "generated")
        else:
            return self.project_root / "app" / "md_review"
    
    def get_temp_dir(self):
        """获取临时文件目录"""
        if self.workspace_available:
            return get_workspace_path("temp")
        else:
            return self.project_root / "temp"
    
    def get_exports_dir(self):
        """获取导出文件目录"""
        if self.workspace_available:
            return get_workspace_path("exports")
        else:
            return self.project_root / "exports"
    
    def ensure_dirs(self):
        """确保所有必要的目录都存在"""
        dirs = [
            self.get_md_review_dir(),
            self.get_static_dir(),
            self.get_images_dir(),
            self.get_ori_docs_dir(),
            self.get_wechat_articles_dir(),
            self.get_downloaded_images_dir(),
            self.get_json_data_dir(),
            self.get_generated_dir(),
            self.get_temp_dir(),
            self.get_exports_dir()
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_file_path(self, category, filename):
        """获取文件路径"""
        if category == "md_review":
            return self.get_md_review_dir() / filename
        elif category == "static":
            return self.get_static_dir() / filename
        elif category == "images":
            return self.get_images_dir() / filename
        elif category == "ori_docs":
            return self.get_ori_docs_dir() / filename
        elif category == "wechat_articles":
            return self.get_wechat_articles_dir() / filename
        elif category == "json":
            return self.get_json_data_dir() / filename
        elif category == "generated":
            return self.get_generated_dir() / filename
        else:
            raise ValueError(f"未知的文件类别: {category}")
    
    def list_files(self, category, pattern="*"):
        """列出指定类别的文件"""
        if category == "md_review":
            return list(self.get_md_review_dir().glob(pattern))
        elif category == "static":
            return list(self.get_static_dir().glob(pattern))
        elif category == "images":
            return list(self.get_images_dir().glob(pattern))
        elif category == "ori_docs":
            return list(self.get_ori_docs_dir().glob(pattern))
        elif category == "wechat_articles":
            return list(self.get_wechat_articles_dir().glob(pattern))
        elif category == "json":
            return list(self.get_json_data_dir().glob(pattern))
        elif category == "generated":
            return list(self.get_generated_dir().glob(pattern))
        else:
            raise ValueError(f"未知的文件类别: {category}")

# 创建全局路径管理器实例
path_manager = PathManager()

# 便捷函数
def get_md_review_dir():
    return path_manager.get_md_review_dir()

def get_static_dir():
    return path_manager.get_static_dir()

def get_images_dir():
    return path_manager.get_images_dir()

def get_ori_docs_dir():
    return path_manager.get_ori_docs_dir()

def get_wechat_articles_dir():
    return path_manager.get_wechat_articles_dir()

def get_downloaded_images_dir():
    return path_manager.get_downloaded_images_dir()

def get_json_data_dir():
    return path_manager.get_json_data_dir()

def get_generated_dir():
    return path_manager.get_generated_dir()

def get_temp_dir():
    return path_manager.get_temp_dir()

def get_exports_dir():
    return path_manager.get_exports_dir()

def ensure_dirs():
    return path_manager.ensure_dirs()

def get_file_path(category, filename):
    return path_manager.get_file_path(category, filename)

def list_files(category, pattern="*"):
    return path_manager.list_files(category, pattern) 