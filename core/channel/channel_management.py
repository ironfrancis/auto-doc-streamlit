#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
频道管理核心功能模块
提供频道的CRUD操作、数据验证、配置管理等功能
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from ..utils.path_manager import get_json_data_dir

class ChannelManager:
    """频道管理器"""
    
    def __init__(self):
        self.channels_file = get_json_data_dir() / "channels_v3.json"
        self.channels = self._load_channels()
    
    def _load_channels(self) -> List[Dict]:
        """加载频道配置"""
        try:
            if os.path.exists(self.channels_file):
                with open(self.channels_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('channels', [])
            return []
        except Exception as e:
            print(f"加载频道配置失败: {e}")
            return []
    
    def _save_channels(self) -> bool:
        """保存频道配置"""
        try:
            data = {'channels': self.channels}
            print(f"正在保存频道数据到: {self.channels_file}")
            print(f"保存的频道数量: {len(self.channels)}")
            with open(self.channels_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("频道数据保存成功")
            return True
        except Exception as e:
            print(f"保存频道配置失败: {e}")
            return False
    
    def get_all_channels(self) -> List[Dict]:
        """获取所有频道"""
        return self.channels
    
    def get_channel_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取频道"""
        for channel in self.channels:
            if channel.get('name') == name:
                return channel
        return None
    
    def create_channel(self, channel_data: Dict) -> bool:
        """创建新频道"""
        try:
            name = channel_data.get('name', '').strip()
            if not name:
                return False
            
            # 检查名称是否已存在
            if any(channel.get('name') == name for channel in self.channels):
                return False
            
            # 添加时间戳
            channel_data.update({
                'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            self.channels.append(channel_data)
            return self._save_channels()
            
        except Exception as e:
            print(f"创建频道失败: {e}")
            return False
    
    def update_channel(self, old_name: str, updated_data: Dict) -> bool:
        """更新频道"""
        try:
            # 查找要更新的频道
            channel_index = None
            for i, channel in enumerate(self.channels):
                if channel.get('name') == old_name:
                    channel_index = i
                    break
            
            if channel_index is None:
                return False
            
            new_name = updated_data.get('name', '').strip()
            if not new_name:
                return False
            
            # 如果名称改变了，检查新名称是否已存在
            if new_name != old_name:
                if any(channel.get('name') == new_name for channel in self.channels):
                    return False  # 新名称已存在
            
            # 统一更新逻辑：创建新的频道对象
            updated_data['last_modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"更新频道: {old_name} -> {new_name}")
            print(f"更新后的数据: {updated_data}")
            self.channels[channel_index] = updated_data.copy()  # 使用copy避免引用问题
            
            return self._save_channels()
            
        except Exception as e:
            print(f"更新频道失败: {e}")
            return False
    
    def delete_channel(self, name: str) -> bool:
        """删除频道"""
        try:
            # 查找要删除的频道
            for i, channel in enumerate(self.channels):
                if channel.get('name') == name:
                    del self.channels[i]
                    return self._save_channels()
            return False
        except Exception as e:
            print(f"删除频道失败: {e}")
            return False
    
    def copy_channel(self, original_name: str, new_name: str) -> bool:
        """复制频道"""
        try:
            # 查找原始频道
            original_channel = None
            for channel in self.channels:
                if channel.get('name') == original_name:
                    original_channel = channel
                    break
            
            if not original_channel:
                return False
            
            # 检查新名称是否已存在
            if any(channel.get('name') == new_name for channel in self.channels):
                return False
            
            # 复制频道数据
            new_channel = original_channel.copy()
            new_channel['name'] = new_name
            new_channel['created_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_channel['last_modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.channels.append(new_channel)
            return self._save_channels()
            
        except Exception as e:
            print(f"复制频道失败: {e}")
            return False
    
    def validate_channel(self, channel_data: Dict) -> Dict:
        """验证频道数据"""
        errors = []
        warnings = []
        
        # 必填字段检查
        if not channel_data.get('name', '').strip():
            errors.append("频道名称不能为空")
        
        if not channel_data.get('description', '').strip():
            warnings.append("建议填写频道描述")
        
        if not channel_data.get('template'):
            warnings.append("建议选择HTML模板")
        
        if not channel_data.get('llm_endpoint'):
            warnings.append("建议选择LLM端点")
        
        # 名称唯一性检查
        name = channel_data.get('name', '').strip()
        if name and name in self.channels:
            errors.append("频道名称已存在")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_channel_names(self) -> List[str]:
        """获取所有频道名称"""
        return list(self.channels.keys())
    
    def search_channels(self, keyword: str) -> List[Dict]:
        """搜索频道"""
        if not keyword:
            return self.get_all_channels()
        
        results = []
        keyword_lower = keyword.lower()
        
        for channel in self.channels.values():
            if (keyword_lower in channel.get('name', '').lower() or
                keyword_lower in channel.get('description', '').lower()):
                results.append(channel)
        
        return results

# 全局实例
channel_manager = ChannelManager()
