#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel数据处理快捷脚本
一键处理 publish_excel/ 目录下的所有Excel文件
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scripts.comprehensive_excel_processor import process_all_files

def main():
    """主函数"""
    print("🚀 Excel数据处理工具")
    print("=" * 50)
    print("📁 处理目录: scripts/publish_excel/")
    print("📄 输出文件: workspace/data/publish_history_for_calendar.csv")
    print("=" * 50)
    
    try:
        success = process_all_files()
        
        if success:
            print("\n✅ 处理完成！")
            print("📊 数据已更新到 publish_history_for_calendar.csv")
        else:
            print("\n❌ 处理失败！")
            print("请检查错误信息并重试")
            
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        print("请检查文件路径和权限")

if __name__ == "__main__":
    main()
