#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workspace管理页面
提供workspace目录的查看和管理功能
"""

import sys
import os
import json
import streamlit as st
from datetime import datetime
from pathlib import Path
import shutil
import glob

# 添加正确的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from language_manager import init_language, get_text
from path_manager import path_manager, get_workspace_path

T = {
    "zh": {
        "page_title": "Workspace管理",
        "workspace_overview": "Workspace概览",
        "directory_structure": "目录结构",
        "file_count": "文件数量",
        "total_size": "总大小",
        "last_modified": "最后修改",
        "actions": "操作",
        "refresh": "刷新",
        "cleanup": "清理",
        "export": "导出",
        "backup": "备份",
        "restore": "恢复",
        "delete": "删除",
        "confirm_delete": "确认删除",
        "success": "操作成功",
        "error": "操作失败",
        "no_files": "无文件",
        "bytes": "字节",
        "kb": "KB",
        "mb": "MB",
        "gb": "GB"
    },
    "en": {
        "page_title": "Workspace Manager",
        "workspace_overview": "Workspace Overview",
        "directory_structure": "Directory Structure",
        "file_count": "File Count",
        "total_size": "Total Size",
        "last_modified": "Last Modified",
        "actions": "Actions",
        "refresh": "Refresh",
        "cleanup": "Cleanup",
        "export": "Export",
        "backup": "Backup",
        "restore": "Restore",
        "delete": "Delete",
        "confirm_delete": "Confirm Delete",
        "success": "Operation Successful",
        "error": "Operation Failed",
        "no_files": "No Files",
        "bytes": "bytes",
        "kb": "KB",
        "mb": "MB",
        "gb": "GB"
    }
}

def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def get_directory_info(directory):
    """获取目录信息"""
    if not directory.exists():
        return {"file_count": 0, "total_size": 0, "last_modified": None}
    
    file_count = 0
    total_size = 0
    last_modified = None
    
    for item in directory.rglob("*"):
        if item.is_file():
            file_count += 1
            total_size += item.stat().st_size
            item_mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if last_modified is None or item_mtime > last_modified:
                last_modified = item_mtime
    
    return {
        "file_count": file_count,
        "total_size": total_size,
        "last_modified": last_modified
    }

def cleanup_directory(directory):
    """清理目录中的临时文件"""
    cleaned_count = 0
    cleaned_size = 0
    
    if not directory.exists():
        return cleaned_count, cleaned_size
    
    # 清理临时文件
    temp_patterns = ["*.tmp", "*.temp", "*.cache", "*.log"]
    for pattern in temp_patterns:
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                file_path.unlink()
                cleaned_count += 1
                cleaned_size += file_size
    
    return cleaned_count, cleaned_size

def main():
    """主函数"""
    init_language()
    
    st.set_page_config(page_title=get_text("page_title"), layout="wide")
    st.title("📁 " + get_text("page_title"))
    
    # 检查workspace是否可用
    if not path_manager.workspace_available:
        st.error("❌ Workspace不可用，请检查workspace_config.py文件")
        return
    
    # 侧边栏操作
    with st.sidebar:
        st.subheader("🛠️ " + get_text("actions"))
        
        if st.button("🔄 " + get_text("refresh")):
            st.rerun()
        
        if st.button("🧹 " + get_text("cleanup")):
            with st.spinner("正在清理..."):
                total_cleaned = 0
                total_size = 0
                for category, dirs in path_manager.workspace_dirs.items():
                    if isinstance(dirs, dict):
                        for name, path in dirs.items():
                            cleaned, size = cleanup_directory(path)
                            total_cleaned += cleaned
                            total_size += size
                    else:
                        cleaned, size = cleanup_directory(dirs)
                        total_cleaned += cleaned
                        total_size += size
                
                st.success(f"✅ 清理完成！删除了 {total_cleaned} 个文件，释放了 {format_size(total_size)} 空间")
    
    # 主内容区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 " + get_text("workspace_overview"))
        
        # 显示目录结构
        for category, dirs in path_manager.workspace_dirs.items():
            with st.expander(f"📁 {category.upper()}", expanded=True):
                if isinstance(dirs, dict):
                    for name, path in dirs.items():
                        info = get_directory_info(path)
                        col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                        
                        with col_a:
                            st.write(f"**{name}:** {path}")
                        
                        with col_b:
                            st.write(f"{info['file_count']} 文件")
                        
                        with col_c:
                            st.write(format_size(info['total_size']))
                        
                        with col_d:
                            if info['last_modified']:
                                st.write(info['last_modified'].strftime("%Y-%m-%d"))
                            else:
                                st.write("-")
                else:
                    info = get_directory_info(dirs)
                    col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                    
                    with col_a:
                        st.write(f"**{category}:** {dirs}")
                    
                    with col_b:
                        st.write(f"{info['file_count']} 文件")
                    
                    with col_c:
                        st.write(format_size(info['total_size']))
                    
                    with col_d:
                        if info['last_modified']:
                            st.write(info['last_modified'].strftime("%Y-%m-%d"))
                        else:
                            st.write("-")
    
    with col2:
        st.subheader("📈 统计信息")
        
        # 计算总体统计
        total_files = 0
        total_size = 0
        
        for category, dirs in path_manager.workspace_dirs.items():
            if isinstance(dirs, dict):
                for name, path in dirs.items():
                    info = get_directory_info(path)
                    total_files += info['file_count']
                    total_size += info['total_size']
            else:
                info = get_directory_info(dirs)
                total_files += info['file_count']
                total_size += info['total_size']
        
        st.metric("📄 总文件数", total_files)
        st.metric("💾 总大小", format_size(total_size))
        
        # 显示最大的目录
        st.subheader("📊 最大目录")
        largest_dirs = []
        
        for category, dirs in path_manager.workspace_dirs.items():
            if isinstance(dirs, dict):
                for name, path in dirs.items():
                    info = get_directory_info(path)
                    if info['total_size'] > 0:
                        largest_dirs.append((name, info['total_size']))
            else:
                info = get_directory_info(dirs)
                if info['total_size'] > 0:
                    largest_dirs.append((category, info['total_size']))
        
        largest_dirs.sort(key=lambda x: x[1], reverse=True)
        
        for name, size in largest_dirs[:5]:
            st.write(f"• {name}: {format_size(size)}")
    
    # 文件浏览器
    st.subheader("🔍 文件浏览器")
    
    # 选择目录
    dir_options = {}
    for category, dirs in path_manager.workspace_dirs.items():
        if isinstance(dirs, dict):
            for name, path in dirs.items():
                dir_options[f"{category}/{name}"] = path
        else:
            dir_options[category] = dirs
    
    selected_dir_key = st.selectbox("选择目录", list(dir_options.keys()))
    selected_dir = dir_options[selected_dir_key]
    
    if selected_dir.exists():
        # 显示文件列表
        files = list(selected_dir.rglob("*"))
        files = [f for f in files if f.is_file()]
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if files:
            st.write(f"**{len(files)} 个文件**")
            
            # 分页显示
            items_per_page = 20
            total_pages = (len(files) + items_per_page - 1) // items_per_page
            
            if total_pages > 1:
                page = st.selectbox("页码", range(1, total_pages + 1)) - 1
            else:
                page = 0
            
            start_idx = page * items_per_page
            end_idx = min(start_idx + items_per_page, len(files))
            
            for file_path in files[start_idx:end_idx]:
                try:
                    stat = file_path.stat()
                    rel_path = file_path.relative_to(selected_dir)
                    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                    
                    with col1:
                        st.write(f"📄 {rel_path}")
                    
                    with col2:
                        st.write(format_size(stat.st_size))
                    
                    with col3:
                        st.write(datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"))
                    
                    with col4:
                        if st.button("🗑️", key=f"del_{file_path.name}"):
                            try:
                                file_path.unlink()
                                st.success("✅ 文件已删除")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ 删除失败: {e}")
                except Exception as e:
                    st.error(f"读取文件信息失败: {e}")
        else:
            st.info("📁 目录为空")
    else:
        st.warning("⚠️ 目录不存在")

if __name__ == "__main__":
    main() 