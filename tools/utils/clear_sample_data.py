#!/usr/bin/env python3
"""
清空示例数据脚本
用于删除示例数据，让用户从零开始录入真实数据
"""

import json
import os
from datetime import datetime

def backup_current_data():
    """备份当前数据"""
    data_file = "workspace/data/json/channel_publish_history.json"
    if os.path.exists(data_file):
        backup_file = f"workspace/data/json/channel_publish_history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 当前数据已备份到: {backup_file}")
        return True
    else:
        print("❌ 数据文件不存在")
        return False

def clear_sample_data():
    """清空示例数据"""
    data_file = "workspace/data/json/channel_publish_history.json"
    
    # 创建空的数据结构
    empty_data = []
    
    # 写入空数据
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(empty_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 示例数据已清空")
    print("📝 现在您可以开始录入真实的频道发布数据")

def show_backup_info():
    """显示备份信息"""
    print("\n📋 备份信息:")
    backup_files = []
    for file in os.listdir("workspace/data/json"):
        if file.startswith("channel_publish_history_backup_") and file.endswith(".json"):
            backup_files.append(file)
    
    if backup_files:
        for file in sorted(backup_files, reverse=True):
            file_path = os.path.join("workspace/data/json", file)
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"  📄 {file} ({file_size} bytes, {file_time.strftime('%Y-%m-%d %H:%M:%S')})")
    else:
        print("  ❌ 没有找到备份文件")

def main():
    """主函数"""
    print("🗑️ 清空示例数据工具")
    print("=" * 50)
    
    # 检查当前数据
    data_file = "workspace/data/json/channel_publish_history.json"
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 当前数据统计:")
        print(f"  频道数: {len(data)}")
        total_records = sum(len(channel['publish_records']) for channel in data)
        print(f"  记录数: {total_records}")
        
        if total_records > 0:
            print("\n⚠️ 警告: 这将删除所有现有数据!")
            confirm = input("确认要清空数据吗? (输入 'yes' 确认): ")
            
            if confirm.lower() == 'yes':
                # 备份数据
                if backup_current_data():
                    # 清空数据
                    clear_sample_data()
                    show_backup_info()
                    
                    print("\n🎉 操作完成!")
                    print("💡 下一步:")
                    print("  1. 访问 '数据录入' 页面添加您的频道")
                    print("  2. 开始录入真实的发布记录")
                    print("  3. 在 '频道发布历史记录' 页面查看效果")
                else:
                    print("❌ 备份失败，操作已取消")
            else:
                print("❌ 操作已取消")
        else:
            print("✅ 数据已经是空的，无需清空")
    else:
        print("✅ 数据文件不存在，可以开始录入新数据")

if __name__ == "__main__":
    main() 