#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化路径管理器
替代复杂的os.path.dirname嵌套
"""

import os
import sys
from pathlib import Path

# 自动检测项目根目录
def get_project_root():
    """获取项目根目录的绝对路径"""
    current_file = Path(__file__).resolve()
    return current_file.parent

# 项目根目录
PROJECT_ROOT = get_project_root()

# 添加项目根目录到Python路径
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 添加核心目录到Python路径
CORE_DIR = PROJECT_ROOT / "core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

# 添加核心子目录到Python路径
CORE_CHANNEL_DIR = CORE_DIR / "channel"
if str(CORE_CHANNEL_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_CHANNEL_DIR))

CORE_WECHAT_DIR = CORE_DIR / "wechat"
if str(CORE_WECHAT_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_WECHAT_DIR))

CORE_APP_DIR = CORE_DIR / "app"
if str(CORE_APP_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_APP_DIR))

CORE_UTILS_DIR = CORE_DIR / "utils"
if str(CORE_UTILS_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_UTILS_DIR))

# 常用目录路径
CONFIG_DIR = PROJECT_ROOT / "workspace" / "data" / "json"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
MD_REVIEW_DIR = WORKSPACE_DIR / "articles" / "md_review"
IMAGES_DIR = WORKSPACE_DIR / "images"
EXPORTS_DIR = WORKSPACE_DIR / "exports"
ARTICLES_DIR = WORKSPACE_DIR / "articles"

def ensure_dir(path):
    """确保目录存在"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

# 创建必要的目录
for dir_path in [CONFIG_DIR, TEMPLATES_DIR, STATIC_DIR, WORKSPACE_DIR, 
                 MD_REVIEW_DIR, IMAGES_DIR, EXPORTS_DIR, ARTICLES_DIR]:
    ensure_dir(dir_path)

# 为了兼容性，提供字符串路径
def get_config_dir():
    return str(CONFIG_DIR)

def get_templates_dir():
    return str(TEMPLATES_DIR)

def get_static_dir():
    return str(STATIC_DIR)

def get_workspace_dir():
    return str(WORKSPACE_DIR)

def get_md_review_dir():
    return str(MD_REVIEW_DIR)

def get_images_dir():
    return str(IMAGES_DIR)

def get_exports_dir():
    return str(EXPORTS_DIR)

def get_articles_dir():
    return str(ARTICLES_DIR)

def get_json_data_dir():
    return get_config_dir()

def get_ori_docs_dir():
    return get_workspace_dir()

if __name__ == "__main__":
    print("项目路径配置:")
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"配置目录: {CONFIG_DIR}")
    print(f"模板目录: {TEMPLATES_DIR}")
    print(f"静态文件目录: {STATIC_DIR}")
    print(f"工作空间目录: {WORKSPACE_DIR}")

