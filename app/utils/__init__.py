# Utils package initialization 
import sys
from pathlib import Path
import os

def get_project_root() -> Path:
    """获取项目根目录的路径"""
    # 当前文件的目录
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    # 项目根目录（当前文件的父目录的父目录）
    project_root = current_dir.parent.parent
    return project_root

__all__ = ['get_project_root'] 