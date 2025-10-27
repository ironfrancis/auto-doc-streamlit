#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
频道更新管理器
用于批量更新所有频道数据，检查Cookie状态等
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

try:
    from core.channel.channel_management import ChannelManager
    from core.wechat.cookie_manager import CookieManager
    from core.utils.path_manager import get_json_data_dir
except ImportError as e:
    print(f"导入依赖模块失败: {e}")


class ChannelUpdateManager:
    """频道更新管理器类"""
    
    def __init__(self):
        """初始化频道更新管理器"""
        self.channel_manager = ChannelManager()
        self.cookie_manager = CookieManager()
        
        # 配置文件路径
        self.config_dir = get_json_data_dir()
        self.channels_file = self.config_dir / "channels_v3.json"
        self.cookies_file = Path("workspace/data/json/cookies_config.json")
        
    def update_all_channels(self) -> Dict[str, Dict]:
        """
        更新所有频道的数据
        
        Returns:
            包含每个频道更新结果的字典
        """
        results = {}
        
        try:
            # 获取所有频道
            channels = self.channel_manager.get_all_channels()
            
            if not channels:
                return {
                    "error": {
                        "status": "error",
                        "message": "没有找到任何频道配置",
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
            
            # 逐个更新频道
            for channel in channels:
                channel_name = channel.get('name', '未知频道')
                
                try:
                    # 检查频道的Cookie状态
                    cookie_status = self._check_channel_cookie(channel_name)
                    
                    if cookie_status['status'] == 'expired':
                        results[channel_name] = {
                            "status": "error",
                            "message": f"Cookie已过期，需要重新登录",
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "cookie_status": cookie_status
                        }
                        continue
                    
                    # 模拟更新过程（这里可以添加实际的数据更新逻辑）
                    update_result = self._update_channel_data(channel_name, channel)
                    
                    if update_result:
                        results[channel_name] = {
                            "status": "success",
                            "message": "频道数据更新成功",
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "cookie_status": cookie_status
                        }
                    else:
                        results[channel_name] = {
                            "status": "error",
                            "message": "频道数据更新失败",
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "cookie_status": cookie_status
                        }
                        
                except Exception as e:
                    results[channel_name] = {
                        "status": "error",
                        "message": f"更新过程中发生错误: {str(e)}",
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            
            return results
            
        except Exception as e:
            return {
                "error": {
                    "status": "error",
                    "message": f"批量更新失败: {str(e)}",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
    
    def _check_channel_cookie(self, channel_name: str) -> Dict:
        """
        检查指定频道的Cookie状态
        
        Args:
            channel_name: 频道名称
            
        Returns:
            Cookie状态信息
        """
        try:
            return self.cookie_manager.get_cookie_status(channel_name)
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查Cookie状态失败: {str(e)}",
                "is_expired": True
            }
    
    def _update_channel_data(self, channel_name: str, channel_config: Dict) -> bool:
        """
        更新指定频道的数据
        
        Args:
            channel_name: 频道名称
            channel_config: 频道配置
            
        Returns:
            是否更新成功
        """
        try:
            # 这里可以添加实际的数据更新逻辑
            # 比如：
            # 1. 获取最新文章数据
            # 2. 更新发布历史
            # 3. 更新统计信息
            # 4. 保存到数据文件
            
            # 目前只是模拟更新过程
            print(f"正在更新频道: {channel_name}")
            
            # 更新频道的最后更新时间
            updated_config = channel_config.copy()
            updated_config['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 保存更新后的配置（这里使用channel_manager来保存）
            return self.channel_manager.update_channel(channel_name, updated_config)
            
        except Exception as e:
            print(f"更新频道 {channel_name} 失败: {e}")
            return False
    
    def check_cookie_status(self) -> Dict[str, str]:
        """
        检查所有频道的Cookie状态
        
        Returns:
            包含每个频道Cookie状态的字典
        """
        status_results = {}
        
        try:
            # 获取所有频道
            channels = self.channel_manager.get_all_channels()
            
            if not channels:
                return {"error": "没有找到任何频道配置"}
            
            # 检查每个频道的Cookie状态
            for channel in channels:
                channel_name = channel.get('name', '未知频道')
                
                try:
                    cookie_status = self.cookie_manager.get_cookie_status(channel_name)
                    
                    if cookie_status['is_expired']:
                        status_results[channel_name] = 'expired'
                    elif cookie_status['status'] == 'fresh':
                        status_results[channel_name] = 'valid'
                    elif cookie_status['status'] == 'warning':
                        status_results[channel_name] = 'warning'
                    else:
                        status_results[channel_name] = 'unknown'
                        
                except Exception as e:
                    status_results[channel_name] = 'error'
            
            return status_results
            
        except Exception as e:
            return {"error": f"检查Cookie状态失败: {str(e)}"}
    
    def get_channel_summary(self) -> Dict:
        """
        获取频道概览信息
        
        Returns:
            频道概览信息
        """
        try:
            channels = self.channel_manager.get_all_channels()
            cookie_status = self.check_cookie_status()
            
            # 统计信息
            total_channels = len(channels)
            valid_cookies = len([s for s in cookie_status.values() if s == 'valid'])
            expired_cookies = len([s for s in cookie_status.values() if s == 'expired'])
            warning_cookies = len([s for s in cookie_status.values() if s == 'warning'])
            
            return {
                "total_channels": total_channels,
                "cookie_status": {
                    "valid": valid_cookies,
                    "expired": expired_cookies,
                    "warning": warning_cookies,
                    "error": len([s for s in cookie_status.values() if s == 'error'])
                },
                "channels": [channel.get('name', '未知') for channel in channels],
                "last_check": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                "error": f"获取频道概览失败: {str(e)}",
                "last_check": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def update_single_channel(self, channel_name: str) -> Dict:
        """
        更新单个频道
        
        Args:
            channel_name: 频道名称
            
        Returns:
            更新结果
        """
        try:
            # 查找频道配置
            channel = self.channel_manager.get_channel_by_name(channel_name)
            
            if not channel:
                return {
                    "status": "error",
                    "message": f"未找到频道: {channel_name}",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # 检查Cookie状态
            cookie_status = self._check_channel_cookie(channel_name)
            
            if cookie_status['status'] == 'expired':
                return {
                    "status": "error",
                    "message": f"Cookie已过期，需要重新登录",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "cookie_status": cookie_status
                }
            
            # 更新频道数据
            update_result = self._update_channel_data(channel_name, channel)
            
            if update_result:
                return {
                    "status": "success",
                    "message": "频道数据更新成功",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "cookie_status": cookie_status
                }
            else:
                return {
                    "status": "error",
                    "message": "频道数据更新失败",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "cookie_status": cookie_status
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"更新频道失败: {str(e)}",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }


# 使用示例
if __name__ == "__main__":
    # 创建频道更新管理器实例
    update_manager = ChannelUpdateManager()
    
    # 检查所有频道的Cookie状态
    print("检查Cookie状态...")
    cookie_status = update_manager.check_cookie_status()
    print("Cookie状态:", cookie_status)
    
    # 获取频道概览
    print("\n获取频道概览...")
    summary = update_manager.get_channel_summary()
    print("频道概览:", summary)
    
    # 更新所有频道（注意：这可能需要较长时间）
    # print("\n更新所有频道...")
    # results = update_manager.update_all_channels()
    # print("更新结果:", results)
