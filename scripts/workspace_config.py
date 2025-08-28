#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workspace配置文件
定义所有数据目录的路径，统一管理workspace目录结构
"""

import os
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent
WORKSPACE_ROOT = PROJECT_ROOT / "workspace"

# Workspace目录结构
WORKSPACE_DIRS = {
    # 文章相关目录
    "articles": {
        "root": WORKSPACE_ROOT / "articles",
        "md_review": WORKSPACE_ROOT / "articles" / "md_review",
        "ori_docs": WORKSPACE_ROOT / "articles" / "ori_docs", 
        "wechat_articles": WORKSPACE_ROOT / "articles" / "wechat_articles",
        "generated": WORKSPACE_ROOT / "articles" / "generated"
    },
    
    # 图片相关目录
    "images": {
        "root": WORKSPACE_ROOT / "images",
        "downloaded": WORKSPACE_ROOT / "images" / "downloaded",
        "processed": WORKSPACE_ROOT / "images" / "processed",
        "thumbnails": WORKSPACE_ROOT / "images" / "thumbnails"
    },
    
    # 数据相关目录
    "data": {
        "root": WORKSPACE_ROOT / "data",
        "json": WORKSPACE_ROOT / "data" / "json",
        "html": WORKSPACE_ROOT / "data" / "html",
        "exports": WORKSPACE_ROOT / "data" / "exports"
    },
    
    # 其他目录
    "exports": WORKSPACE_ROOT / "exports",
    "temp": WORKSPACE_ROOT / "temp"
}

def ensure_workspace_dirs():
    """确保所有workspace目录都存在"""
    for category, dirs in WORKSPACE_DIRS.items():
        if isinstance(dirs, dict):
            for name, path in dirs.items():
                path.mkdir(parents=True, exist_ok=True)
        else:
            dirs.mkdir(parents=True, exist_ok=True)

def get_workspace_path(category, subcategory=None):
    """获取workspace路径"""
    if subcategory:
        return WORKSPACE_DIRS[category][subcategory]
    else:
        return WORKSPACE_DIRS[category]

def get_legacy_path_mapping():
    """获取旧路径到新路径的映射"""
    return {
        "app/md_review": WORKSPACE_DIRS["articles"]["md_review"],
        "app/static": WORKSPACE_DIRS["data"]["html"],
        "app/static/images": WORKSPACE_DIRS["images"]["processed"],
        "ori_docs": WORKSPACE_DIRS["articles"]["ori_docs"],
        "wechat_articles": WORKSPACE_DIRS["articles"]["wechat_articles"],
        "downloaded_images": WORKSPACE_DIRS["images"]["downloaded"]
    }

# 初始化时确保目录存在
ensure_workspace_dirs()

if __name__ == "__main__":
    print("Workspace目录结构:")
    for category, dirs in WORKSPACE_DIRS.items():
        print(f"\n{category}:")
        if isinstance(dirs, dict):
            for name, path in dirs.items():
                print(f"  {name}: {path}")
        else:
            print(f"  {dirs}") 