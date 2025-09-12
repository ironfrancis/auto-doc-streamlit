#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown文件迁移脚本
将app/md_review目录中的新文件迁移到workspace/articles/md_review目录
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def migrate_md_files():
    """迁移Markdown文件"""
    
    # 定义路径
    old_dir = Path("app/md_review")
    new_dir = Path("workspace/articles/md_review")
    
    # 检查目录是否存在
    if not old_dir.exists():
        print(f"❌ 旧目录不存在: {old_dir}")
        return
    
    if not new_dir.exists():
        print(f"❌ 新目录不存在: {new_dir}")
        return
    
    print(f"📁 开始迁移Markdown文件...")
    print(f"📂 源目录: {old_dir}")
    print(f"📂 目标目录: {new_dir}")
    print("-" * 50)
    
    # 获取旧目录中的所有.md文件
    old_files = list(old_dir.glob("*.md"))
    
    if not old_files:
        print("ℹ️  旧目录中没有找到.md文件")
        return
    
    # 获取新目录中已存在的文件
    existing_files = {f.name for f in new_dir.glob("*.md")}
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for old_file in old_files:
        try:
            # 检查文件是否已存在于新目录
            if old_file.name in existing_files:
                print(f"⏭️  跳过已存在的文件: {old_file.name}")
                skipped_count += 1
                continue
            
            # 复制文件到新目录
            new_file = new_dir / old_file.name
            shutil.copy2(old_file, new_file)
            
            # 验证复制是否成功
            if new_file.exists() and new_file.stat().st_size == old_file.stat().st_size:
                print(f"✅ 成功迁移: {old_file.name}")
                migrated_count += 1
            else:
                print(f"❌ 迁移失败: {old_file.name}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ 迁移出错 {old_file.name}: {str(e)}")
            error_count += 1
    
    print("-" * 50)
    print(f"📊 迁移完成！")
    print(f"✅ 成功迁移: {migrated_count} 个文件")
    print(f"⏭️  跳过重复: {skipped_count} 个文件")
    print(f"❌ 迁移失败: {error_count} 个文件")
    
    if migrated_count > 0:
        print(f"\n💡 建议：迁移完成后可以删除旧目录 {old_dir}")
        print(f"💡 命令：rm -rf {old_dir}")

def backup_old_directory():
    """备份旧目录（可选）"""
    old_dir = Path("app/md_review")
    if old_dir.exists():
        backup_dir = Path(f"app/md_review_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        try:
            shutil.copytree(old_dir, backup_dir)
            print(f"💾 已备份旧目录到: {backup_dir}")
        except Exception as e:
            print(f"❌ 备份失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 Markdown文件迁移工具")
    print("=" * 50)
    
    # 询问是否要备份
    backup_choice = input("是否要备份旧目录？(y/N): ").strip().lower()
    if backup_choice == 'y':
        backup_old_directory()
        print()
    
    # 执行迁移
    migrate_md_files()
    
    print("\n🎉 迁移完成！")
