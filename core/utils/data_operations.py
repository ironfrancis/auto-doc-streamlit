#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据操作功能模块
提供端点信息加载、模板文件管理、数据导入导出等功能
"""

import json
import os
import pandas as pd
from typing import Dict, List, Optional, Any
from path_manager import get_json_data_dir

def load_endpoints() -> List[Dict]:
    """加载LLM端点配置"""
    try:
        endpoints_path = get_json_data_dir() / "llm_endpoints.json"
        if os.path.exists(endpoints_path):
            with open(endpoints_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"加载端点配置失败: {e}")
        return []

def get_template_files(template_dir: str = "static/templates") -> List[str]:
    """获取HTML模板文件列表"""
    try:
        if os.path.exists(template_dir):
            return [f for f in os.listdir(template_dir) if f.endswith('.html')]
        return []
    except Exception as e:
        print(f"获取模板文件失败: {e}")
        return []

def get_endpoint_names(endpoints: List[Dict]) -> List[str]:
    """获取端点名称列表"""
    return [ep["name"] for ep in endpoints] if endpoints else []

def get_endpoint_by_name(endpoints: List[Dict], name: str) -> Optional[Dict]:
    """根据名称获取端点配置"""
    return next((ep for ep in endpoints if ep["name"] == name), None)

def export_channels_data(channels: List[Dict], filename: str = None) -> str:
    """导出频道数据"""
    try:
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"channels_export_{timestamp}.json"
        
        export_data = {
            'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_channels': len(channels),
            'channels': channels
        }
        
        export_path = get_json_data_dir() / filename
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return str(export_path)
        
    except Exception as e:
        print(f"导出频道数据失败: {e}")
        return ""

def import_channels_data(file_content: str) -> Dict:
    """导入频道数据"""
    try:
        # 尝试解析JSON
        data = json.loads(file_content)
        
        # 验证数据格式
        if 'channels' not in data:
            return {
                'success': False,
                'error': '文件格式不正确，缺少channels字段'
            }
        
        channels = data['channels']
        if not isinstance(channels, list):
            return {
                'success': False,
                'error': 'channels字段必须是数组格式'
            }
        
        # 验证每个频道数据
        valid_channels = []
        invalid_channels = []
        
        for i, channel in enumerate(channels):
            if isinstance(channel, dict) and 'name' in channel:
                valid_channels.append(channel)
            else:
                invalid_channels.append(f"第{i+1}个频道数据格式不正确")
        
        return {
            'success': True,
            'valid_channels': valid_channels,
            'invalid_channels': invalid_channels,
            'total': len(channels),
            'valid_count': len(valid_channels),
            'invalid_count': len(invalid_channels)
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'JSON格式错误: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'导入失败: {str(e)}'
        }

def export_prompt_blocks(blocks: Dict, filename: str = None) -> str:
    """导出提示词块数据"""
    try:
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prompt_blocks_export_{timestamp}.json"
        
        export_data = {
            'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_blocks': len(blocks),
            'blocks': blocks
        }
        
        export_path = get_json_data_dir() / filename
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return str(export_path)
        
    except Exception as e:
        print(f"导出提示词块数据失败: {e}")
        return ""

def import_prompt_blocks(file_content: str) -> Dict:
    """导入提示词块数据"""
    try:
        # 尝试解析JSON
        data = json.loads(file_content)
        
        # 验证数据格式
        if 'blocks' not in data:
            return {
                'success': False,
                'error': '文件格式不正确，缺少blocks字段'
            }
        
        blocks = data['blocks']
        if not isinstance(blocks, dict):
            return {
                'success': False,
                'error': 'blocks字段必须是对象格式'
            }
        
        # 验证每个块数据
        valid_blocks = {}
        invalid_blocks = []
        
        for block_id, block in blocks.items():
            if isinstance(block, dict) and 'name' in block and 'content' in block:
                valid_blocks[block_id] = block
            else:
                invalid_blocks.append(f"块 {block_id} 数据格式不正确")
        
        return {
            'success': True,
            'valid_blocks': valid_blocks,
            'invalid_blocks': invalid_blocks,
            'total': len(blocks),
            'valid_count': len(valid_blocks),
            'invalid_count': len(invalid_blocks)
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'JSON格式错误: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'导入失败: {str(e)}'
        }

def export_to_csv(data: List[Dict], filename: str = None) -> str:
    """导出数据到CSV"""
    try:
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data_export_{timestamp}.csv"
        
        df = pd.DataFrame(data)
        export_path = get_json_data_dir() / filename
        df.to_csv(export_path, index=False, encoding='utf-8-sig')
        
        return str(export_path)
        
    except Exception as e:
        print(f"导出CSV失败: {e}")
        return ""

def backup_data(backup_name: str = None) -> str:
    """备份数据"""
    try:
        if backup_name is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
        
        backup_dir = get_json_data_dir() / "backups" / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份频道数据
        channels_file = get_json_data_dir() / "channels_new.json"
        if os.path.exists(channels_file):
            backup_channels = backup_dir / "channels_new.json"
            with open(channels_file, 'r', encoding='utf-8') as src, \
                 open(backup_channels, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        # 备份提示词块数据
        blocks_file = get_json_data_dir() / "prompt_blocks.json"
        if os.path.exists(blocks_file):
            backup_blocks = backup_dir / "prompt_blocks.json"
            with open(blocks_file, 'r', encoding='utf-8') as src, \
                 open(backup_blocks, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        # 备份端点配置
        endpoints_file = get_json_data_dir() / "llm_endpoints.json"
        if os.path.exists(endpoints_file):
            backup_endpoints = backup_dir / "llm_endpoints.json"
            with open(endpoints_file, 'r', encoding='utf-8') as src, \
                 open(backup_endpoints, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        return str(backup_dir)
        
    except Exception as e:
        print(f"备份数据失败: {e}")
        return ""

def restore_data(backup_path: str) -> Dict:
    """恢复数据"""
    try:
        backup_dir = os.path.join(backup_path)
        if not os.path.exists(backup_dir):
            return {
                'success': False,
                'error': '备份目录不存在'
            }
        
        restored_files = []
        
        # 恢复频道数据
        backup_channels = os.path.join(backup_dir, "channels_v3.json")
        if os.path.exists(backup_channels):
            channels_file = get_json_data_dir() / "channels_v3.json"
            with open(backup_channels, 'r', encoding='utf-8') as src, \
                 open(channels_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            restored_files.append("channels_v3.json")
        
        # 恢复提示词块数据
        backup_blocks = os.path.join(backup_dir, "prompt_blocks.json")
        if os.path.exists(backup_blocks):
            blocks_file = get_json_data_dir() / "prompt_blocks.json"
            with open(backup_blocks, 'r', encoding='utf-8') as src, \
                 open(blocks_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            restored_files.append("prompt_blocks.json")
        
        # 恢复端点配置
        backup_endpoints = os.path.join(backup_dir, "llm_endpoints.json")
        if os.path.exists(backup_endpoints):
            endpoints_file = get_json_data_dir() / "llm_endpoints.json"
            with open(backup_endpoints, 'r', encoding='utf-8') as src, \
                 open(endpoints_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            restored_files.append("llm_endpoints.json")
        
        return {
            'success': True,
            'restored_files': restored_files,
            'total_restored': len(restored_files)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'恢复数据失败: {str(e)}'
        }

def get_data_statistics() -> Dict:
    """获取数据统计信息"""
    try:
        stats = {
            'channels_count': 0,
            'prompt_blocks_count': 0,
            'endpoints_count': 0,
            'templates_count': 0,
            'last_backup': None,
            'data_size': 0
        }
        
        # 统计频道数量
        channels_file = get_json_data_dir() / "channels_v3.json"
        if os.path.exists(channels_file):
            with open(channels_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats['channels_count'] = len(data.get('channels', {}))
                stats['data_size'] += os.path.getsize(channels_file)
        
        # 统计提示词块数量
        blocks_file = get_json_data_dir() / "prompt_blocks.json"
        if os.path.exists(blocks_file):
            with open(blocks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats['prompt_blocks_count'] = len(data)
                stats['data_size'] += os.path.getsize(blocks_file)
        
        # 统计端点数量
        endpoints_file = get_json_data_dir() / "llm_endpoints.json"
        if os.path.exists(endpoints_file):
            with open(endpoints_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats['endpoints_count'] = len(data)
                stats['data_size'] += os.path.getsize(endpoints_file)
        
        # 统计模板数量
        template_dir = "static/templates"
        if os.path.exists(template_dir):
            stats['templates_count'] = len([f for f in os.listdir(template_dir) if f.endswith('.html')])
        
        # 查找最新备份
        backup_dir = get_json_data_dir() / "backups"
        if os.path.exists(backup_dir):
            backups = [d for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d))]
            if backups:
                latest_backup = max(backups, key=lambda x: os.path.getctime(os.path.join(backup_dir, x)))
                stats['last_backup'] = latest_backup
        
        return stats
        
    except Exception as e:
        print(f"获取数据统计失败: {e}")
        return {}
