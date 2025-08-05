#!/usr/bin/env python3
"""
频道发布数据采集工具
支持从多个渠道自动或手动采集发布数据
"""

import json
import os
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional

class ChannelDataCollector:
    """频道数据采集器"""
    
    def __init__(self, data_file: str = "workspace/data/json/channel_publish_history.json"):
        self.data_file = data_file
        self.channels_data = self.load_data()
    
    def load_data(self) -> List[Dict]:
        """加载现有数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_data(self):
        """保存数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.channels_data, f, ensure_ascii=False, indent=2)
    
    def add_channel(self, channel_name: str, description: str = ""):
        """添加新频道"""
        # 检查频道是否已存在
        for channel in self.channels_data:
            if channel['channel_name'] == channel_name:
                print(f"频道 '{channel_name}' 已存在")
                return
        
        new_channel = {
            "channel_name": channel_name,
            "description": description,
            "publish_records": []
        }
        self.channels_data.append(new_channel)
        self.save_data()
        print(f"✅ 频道 '{channel_name}' 添加成功")
    
    def delete_channel(self, channel_name: str):
        """删除频道"""
        for i, channel in enumerate(self.channels_data):
            if channel['channel_name'] == channel_name:
                deleted_channel = self.channels_data.pop(i)
                self.save_data()
                print(f"✅ 频道 '{channel_name}' 删除成功")
                return True
        print(f"❌ 频道 '{channel_name}' 不存在")
        return False
    
    def delete_record(self, channel_name: str, record_id: str):
        """删除发布记录"""
        for channel in self.channels_data:
            if channel['channel_name'] == channel_name:
                for i, record in enumerate(channel['publish_records']):
                    if record['id'] == record_id:
                        deleted_record = channel['publish_records'].pop(i)
                        self.save_data()
                        print(f"✅ 记录 '{deleted_record.get('title', '未命名')}' 删除成功")
                        return True
                print(f"❌ 记录 {record_id} 不存在")
                return False
        print(f"❌ 频道 '{channel_name}' 不存在")
        return False
    
    def add_publish_record(self, channel_name: str, record: Dict):
        """添加发布记录"""
        for channel in self.channels_data:
            if channel['channel_name'] == channel_name:
                # 生成唯一ID
                if not record.get('id'):
                    record['id'] = f"{len(channel['publish_records']) + 1:03d}"
                
                # 设置默认值
                record.setdefault('views', 0)
                record.setdefault('likes', 0)
                record.setdefault('comments', 0)
                record.setdefault('shares', 0)
                record.setdefault('status', 'published')
                record.setdefault('tags', [])
                
                channel['publish_records'].append(record)
                self.save_data()
                print(f"✅ 发布记录添加成功: {record.get('title', '未命名')}")
                return
        
        print(f"❌ 频道 '{channel_name}' 不存在")
    
    def update_record_metrics(self, channel_name: str, record_id: str, metrics: Dict):
        """更新记录的数据指标"""
        for channel in self.channels_data:
            if channel['channel_name'] == channel_name:
                for record in channel['publish_records']:
                    if record['id'] == record_id:
                        record.update(metrics)
                        self.save_data()
                        print(f"✅ 记录 {record_id} 指标更新成功")
                        return
                print(f"❌ 记录 {record_id} 不存在")
                return
        print(f"❌ 频道 '{channel_name}' 不存在")
    
    def get_channel_records(self, channel_name: str) -> List[Dict]:
        """获取频道的所有记录"""
        for channel in self.channels_data:
            if channel['channel_name'] == channel_name:
                return channel['publish_records']
        return []
    
    def get_all_records(self) -> List[Dict]:
        """获取所有记录"""
        all_records = []
        for channel in self.channels_data:
            for record in channel['publish_records']:
                record['channel_name'] = channel['channel_name']
                all_records.append(record)
        return all_records
    
    def export_to_csv(self, filename: str = None):
        """导出数据为CSV格式"""
        if not filename:
            filename = f"channel_publish_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        all_records = self.get_all_records()
        if all_records:
            df = pd.DataFrame(all_records)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ 数据已导出到: {filename}")
        else:
            print("❌ 没有数据可导出")
    
    def import_from_csv(self, filename: str):
        """从CSV文件导入数据"""
        if not os.path.exists(filename):
            print(f"❌ 文件不存在: {filename}")
            return
        
        try:
            df = pd.read_csv(filename, encoding='utf-8-sig')
            imported_count = 0
            
            for _, row in df.iterrows():
                channel_name = row.get('channel_name', '未知频道')
                record = {
                    'id': str(row.get('id', '')),
                    'title': row.get('title', ''),
                    'publish_date': row.get('publish_date', ''),
                    'publish_time': row.get('publish_time', ''),
                    'status': row.get('status', 'published'),
                    'views': int(row.get('views', 0)),
                    'likes': int(row.get('likes', 0)),
                    'comments': int(row.get('comments', 0)),
                    'shares': int(row.get('shares', 0)),
                    'url': row.get('url', ''),
                    'tags': row.get('tags', '').split(',') if row.get('tags') else []
                }
                
                self.add_publish_record(channel_name, record)
                imported_count += 1
            
            print(f"✅ 成功导入 {imported_count} 条记录")
            
        except Exception as e:
            print(f"❌ 导入失败: {e}")

class ManualDataEntry:
    """手动数据录入工具"""
    
    def __init__(self, collector: ChannelDataCollector):
        self.collector = collector
    
    def add_channel_interactive(self):
        """交互式添加频道"""
        print("\n📺 添加新频道")
        print("=" * 30)
        
        channel_name = input("频道名称: ").strip()
        if not channel_name:
            print("❌ 频道名称不能为空")
            return
        
        description = input("频道描述 (可选): ").strip()
        
        self.collector.add_channel(channel_name, description)
    
    def add_record_interactive(self):
        """交互式添加发布记录"""
        print("\n📝 添加发布记录")
        print("=" * 30)
        
        # 显示现有频道
        channels = [ch['channel_name'] for ch in self.collector.channels_data]
        if not channels:
            print("❌ 请先添加频道")
            return
        
        print("现有频道:")
        for i, channel in enumerate(channels, 1):
            print(f"  {i}. {channel}")
        
        try:
            choice = int(input(f"选择频道 (1-{len(channels)}): ")) - 1
            if 0 <= choice < len(channels):
                channel_name = channels[choice]
            else:
                print("❌ 无效选择")
                return
        except ValueError:
            print("❌ 请输入数字")
            return
        
        # 输入记录信息
        title = input("文章标题: ").strip()
        if not title:
            print("❌ 标题不能为空")
            return
        
        publish_date = input("发布日期 (YYYY-MM-DD): ").strip()
        publish_time = input("发布时间 (HH:MM): ").strip()
        
        # 数据指标
        try:
            views = int(input("浏览量: ") or "0")
            likes = int(input("点赞数: ") or "0")
            comments = int(input("评论数: ") or "0")
            shares = int(input("分享数: ") or "0")
        except ValueError:
            print("❌ 请输入有效的数字")
            return
        
        url = input("文章链接 (可选): ").strip()
        tags = input("标签 (用逗号分隔): ").strip()
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # 状态选择
        status_options = ['published', 'draft', 'scheduled']
        print("状态选项:")
        for i, status in enumerate(status_options, 1):
            print(f"  {i}. {status}")
        
        try:
            status_choice = int(input("选择状态 (1-3): ")) - 1
            status = status_options[status_choice] if 0 <= status_choice < 3 else 'published'
        except ValueError:
            status = 'published'
        
        # 创建记录
        record = {
            'title': title,
            'publish_date': publish_date,
            'publish_time': publish_time,
            'status': status,
            'views': views,
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'url': url,
            'tags': tags_list
        }
        
        self.collector.add_publish_record(channel_name, record)
    
    def update_metrics_interactive(self):
        """交互式更新数据指标"""
        print("\n📊 更新数据指标")
        print("=" * 30)
        
        all_records = self.collector.get_all_records()
        if not all_records:
            print("❌ 没有可更新的记录")
            return
        
        # 显示记录列表
        print("现有记录:")
        for i, record in enumerate(all_records[:10], 1):  # 只显示前10条
            print(f"  {i}. [{record['channel_name']}] {record['title']}")
        
        try:
            choice = int(input(f"选择记录 (1-{min(10, len(all_records))}): ")) - 1
            if 0 <= choice < len(all_records):
                record = all_records[choice]
            else:
                print("❌ 无效选择")
                return
        except ValueError:
            print("❌ 请输入数字")
            return
        
        print(f"\n更新记录: {record['title']}")
        
        # 输入新指标
        try:
            views_input = input(f"新浏览量 (当前: {record['views']}): ")
            views = int(views_input) if views_input.strip() else record['views']
            
            likes_input = input(f"新点赞数 (当前: {record['likes']}): ")
            likes = int(likes_input) if likes_input.strip() else record['likes']
            
            comments_input = input(f"新评论数 (当前: {record['comments']}): ")
            comments = int(comments_input) if comments_input.strip() else record['comments']
            
            shares_input = input(f"新分享数 (当前: {record['shares']}): ")
            shares = int(shares_input) if shares_input.strip() else record['shares']
        except ValueError:
            print("❌ 请输入有效的数字")
            return
        
        metrics = {
            'views': views,
            'likes': likes,
            'comments': comments,
            'shares': shares
        }
        
        self.collector.update_record_metrics(record['channel_name'], record['id'], metrics)

def main():
    """主函数 - 命令行工具"""
    collector = ChannelDataCollector()
    entry = ManualDataEntry(collector)
    
    while True:
        print("\n" + "=" * 50)
        print("📊 频道发布数据采集工具")
        print("=" * 50)
        print("1. 添加频道")
        print("2. 添加发布记录")
        print("3. 更新数据指标")
        print("4. 查看所有记录")
        print("5. 导出数据 (CSV)")
        print("6. 导入数据 (CSV)")
        print("0. 退出")
        print("=" * 50)
        
        choice = input("请选择操作 (0-6): ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
        elif choice == '1':
            entry.add_channel_interactive()
        elif choice == '2':
            entry.add_record_interactive()
        elif choice == '3':
            entry.update_metrics_interactive()
        elif choice == '4':
            all_records = collector.get_all_records()
            if all_records:
                print(f"\n📋 共 {len(all_records)} 条记录:")
                for record in all_records[:5]:  # 只显示前5条
                    print(f"  [{record['channel_name']}] {record['title']} - {record['publish_date']}")
                if len(all_records) > 5:
                    print(f"  ... 还有 {len(all_records) - 5} 条记录")
            else:
                print("❌ 暂无记录")
        elif choice == '5':
            collector.export_to_csv()
        elif choice == '6':
            filename = input("CSV文件路径: ").strip()
            if filename:
                collector.import_from_csv(filename)
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main() 