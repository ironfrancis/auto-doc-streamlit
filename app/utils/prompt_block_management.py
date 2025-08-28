#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词块管理功能模块
提供提示词块的CRUD操作、组合逻辑、最终提示词生成等功能
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# 修复导入路径
try:
    from app.path_manager import get_json_data_dir
except ImportError:
    try:
        from path_manager import get_json_data_dir
    except ImportError:
        # 如果都导入失败，使用默认路径
        def get_json_data_dir():
            return Path("app")

class PromptBlockManager:
    """提示词块管理器"""
    
    def __init__(self):
        # 尝试多个可能的文件路径
        possible_files = [
            get_json_data_dir() / "prompt_blocks.json",
            get_json_data_dir() / "prompt_blocks_config.json",
            Path("app/prompt_blocks_config.json")
        ]
        
        # 找到第一个存在的文件
        self.blocks_file = None
        for file_path in possible_files:
            if os.path.exists(file_path):
                self.blocks_file = file_path
                break
        
        if not self.blocks_file:
            # 如果都不存在，使用默认路径
            self.blocks_file = get_json_data_dir() / "prompt_blocks.json"
        
        self.blocks = self._load_blocks()
    
    def _load_blocks(self) -> Dict:
        """加载提示词块配置"""
        try:
            if os.path.exists(self.blocks_file):
                with open(self.blocks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查数据结构
                if isinstance(data, dict):
                    # 如果是扁平结构（现有格式），转换为嵌套结构
                    if 'prompt_blocks' not in data:
                        # 扁平结构，需要转换
                        converted_data = {}
                        for block_id, block_data in data.items():
                            if isinstance(block_data, dict) and 'category' in block_data:
                                category = block_data['category']
                                if category not in converted_data:
                                    converted_data[category] = {}
                                converted_data[category][block_id] = block_data
                        
                        # 保存转换后的数据
                        self.blocks = converted_data
                        self._save_blocks()  # 保存转换后的结构
                        return converted_data
                    else:
                        # 已经是嵌套结构
                        return data.get('prompt_blocks', {})
                else:
                    return {}
            else:
                return {}
        except Exception as e:
            print(f"加载提示词块配置失败: {e}")
            return {}
    
    def _save_blocks(self) -> bool:
        """保存提示词块配置"""
        try:
            # 确保目录存在
            self.blocks_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存为嵌套结构
            save_data = {
                "prompt_blocks": self.blocks,
                "metadata": {
                    "version": "1.0",
                    "last_modified": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "description": "提示词块配置文件"
                }
            }
            
            with open(self.blocks_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存提示词块配置失败: {e}")
            return False
    
    def get_all_blocks(self) -> Dict:
        """获取所有提示词块"""
        all_blocks = {}
        for category, blocks in self.blocks.items():
            all_blocks.update(blocks)
        return all_blocks
    
    def get_blocks_by_category(self, category: str) -> Dict:
        """根据分类获取提示词块"""
        return self.blocks.get(category, {})
    
    def get_public_blocks(self) -> Dict:
        """获取公共提示词块"""
        return self.get_blocks_by_category('public')
    
    def get_industry_blocks(self) -> Dict:
        """获取行业提示词块"""
        return self.get_blocks_by_category('industry')
    
    def get_block_by_id(self, block_id: str) -> Optional[Dict]:
        """根据ID获取提示词块"""
        for category, blocks in self.blocks.items():
            if block_id in blocks:
                return blocks[block_id]
        return None
    
    def create_block(self, block_data: Dict) -> bool:
        """创建新提示词块"""
        try:
            name = block_data.get('name', '').strip()
            category = block_data.get('category', 'custom')
            
            if not name:
                return False
            
            # 生成唯一ID
            block_id = f"block_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 添加时间戳
            block_data.update({
                'id': block_id,
                'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # 确保分类存在
            if category not in self.blocks:
                self.blocks[category] = {}
            
            # 添加到对应分类
            self.blocks[category][block_id] = block_data
            return self._save_blocks()
            
        except Exception as e:
            print(f"创建提示词块失败: {e}")
            return False
    
    def update_block(self, block_id: str, updated_data: Dict) -> bool:
        """更新提示词块"""
        try:
            # 查找块所在位置
            block_found = False
            for category, blocks in self.blocks.items():
                if block_id in blocks:
                    # 更新数据
                    blocks[block_id].update(updated_data)
                    blocks[block_id]['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    block_found = True
                    break
            
            if not block_found:
                print(f"提示词块 '{block_id}' 不存在")
                return False
            
            return self._save_blocks()
            
        except Exception as e:
            print(f"更新提示词块失败: {e}")
            return False
    
    def delete_block(self, block_id: str) -> bool:
        """删除提示词块"""
        try:
            # 查找并删除块
            block_found = False
            for category, blocks in self.blocks.items():
                if block_id in blocks:
                    del blocks[block_id]
                    block_found = True
                    break
            
            if not block_found:
                print(f"提示词块 '{block_id}' 不存在")
                return False
            
            return self._save_blocks()
            
        except Exception as e:
            print(f"删除提示词块失败: {e}")
            return False
    
    def combine_prompt_blocks(self, selected_block_ids: List[str], custom_blocks: Dict = None) -> str:
        """组合提示词块"""
        try:
            combined_content = []
            
            # 添加选中的提示词块
            for block_id in selected_block_ids:
                block = self.get_block_by_id(block_id)
                if block:
                    content = block.get('content', '')
                    if isinstance(content, dict):
                        # 如果是结构化内容，转换为文本
                        for key, value in content.items():
                            if isinstance(value, list):
                                combined_content.append(f"{key}: {', '.join(value)}")
                            else:
                                combined_content.append(f"{key}: {value}")
                    else:
                        combined_content.append(str(content))
            
            # 添加自定义块
            if custom_blocks:
                for key, block in custom_blocks.items():
                    combined_content.append(f"【{block['name']}】\n{block['content']}")
            
            return "\n\n".join(combined_content)
            
        except Exception as e:
            print(f"组合提示词块失败: {e}")
            return ""
    
    def generate_final_prompt_json(self, selected_block_ids: List[str], custom_blocks: Dict = None, channel_data: Dict = None) -> str:
        """生成最终提示词的JSON格式"""
        try:
            prompt_data = {
                "channel_info": {
                    "name": channel_data.get('name', ''),
                    "description": channel_data.get('description', ''),
                    "template": channel_data.get('template', ''),
                    "llm_endpoint": channel_data.get('llm_endpoint', '')
                },
                "selected_blocks": [],
                "custom_blocks": [],
                "combined_prompt": "",
                "generation_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 添加选中的提示词块信息
            for block_id in selected_block_ids:
                block = self.get_block_by_id(block_id)
                if block:
                    prompt_data["selected_blocks"].append({
                        "id": block_id,
                        "name": block.get('name', ''),
                        "category": block.get('category', ''),
                        "content": block.get('content', '')
                    })
            
            # 添加自定义块信息
            if custom_blocks:
                for key, block in custom_blocks.items():
                    prompt_data["custom_blocks"].append({
                        "key": key,
                        "name": block.get('name', ''),
                        "content": block.get('content', '')
                    })
            
            # 生成组合后的提示词
            prompt_data["combined_prompt"] = self.combine_prompt_blocks(selected_block_ids, custom_blocks)
            
            return json.dumps(prompt_data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"生成最终提示词JSON失败: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)
    
    def validate_block_data(self, block_data: Dict) -> Dict:
        """验证提示词块数据"""
        errors = []
        warnings = []
        
        # 必填字段检查
        if not block_data.get('name', '').strip():
            errors.append("块名称不能为空")
        
        if not block_data.get('description', '').strip():
            warnings.append("建议填写块描述")
        
        if not block_data.get('content'):
            errors.append("块内容不能为空")
        
        if not block_data.get('category'):
            warnings.append("建议选择块分类")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def search_blocks(self, keyword: str) -> Dict:
        """搜索提示词块"""
        if not keyword:
            return self.blocks
        
        results = {}
        keyword_lower = keyword.lower()
        
        for category, blocks in self.blocks.items():
            for block_id, block in blocks.items():
                if (keyword_lower in block.get('name', '').lower() or
                    keyword_lower in block.get('description', '').lower() or
                    keyword_lower in str(block.get('content', '')).lower()):
                    results[f"{category}_{block_id}"] = block # 使用分类和ID组合作为键
        
        return results
    
    def get_block_statistics(self) -> Dict:
        """获取提示词块统计信息"""
        total_blocks = 0
        public_blocks = 0
        industry_blocks = 0
        
        for category, blocks in self.blocks.items():
            total_blocks += len(blocks)
            if category == 'public':
                public_blocks += len(blocks)
            elif category == 'industry':
                industry_blocks += len(blocks)
        
        return {
            'total': total_blocks,
            'public': public_blocks,
            'industry': industry_blocks,
            'custom': total_blocks - public_blocks - industry_blocks
        }

# 全局实例
prompt_block_manager = PromptBlockManager()
