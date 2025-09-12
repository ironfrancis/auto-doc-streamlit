#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词块管理器
用于管理提示词块的读取、组合和生成，支持公共提示词块和行业提示词块
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class PromptBlockManager:
    """提示词块管理器类"""
    
    def __init__(self, config_file: str = "app/prompt_blocks_config.json"):
        """
        初始化提示词块管理器
        
        Args:
            config_file: 提示词块配置文件路径
        """
        self.config_file = Path(config_file)
        self.prompt_blocks_data = self._load_prompt_blocks()
    
    def _load_prompt_blocks(self) -> Dict:
        """加载提示词块配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"加载提示词块配置文件失败: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "prompt_blocks": {
                "public": {},
                "industry": {}
            },
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "description": "提示词块配置文件"
            }
        }
    
    def get_all_blocks(self) -> Dict:
        """获取所有提示词块"""
        return self.prompt_blocks_data.get("prompt_blocks", {})
    
    def get_public_blocks(self) -> Dict:
        """获取公共提示词块"""
        return self.prompt_blocks_data.get("prompt_blocks", {}).get("public", {})
    
    def get_industry_blocks(self) -> Dict:
        """获取行业提示词块"""
        return self.prompt_blocks_data.get("prompt_blocks", {}).get("industry", {})
    
    def get_block_by_id(self, block_id: str) -> Optional[Dict]:
        """根据ID获取提示词块"""
        all_blocks = self.get_all_blocks()
        for category in all_blocks.values():
            if block_id in category:
                return category[block_id]
        return None
    
    def get_blocks_by_category(self, category: str) -> Dict:
        """根据分类获取提示词块"""
        return self.prompt_blocks_data.get("prompt_blocks", {}).get(category, {})
    
    def get_block_names(self, category: str = None) -> List[str]:
        """获取提示词块名称列表"""
        if category:
            blocks = self.get_blocks_by_category(category)
            return [block["name"] for block in blocks.values()]
        else:
            all_blocks = self.get_all_blocks()
            names = []
            for category_blocks in all_blocks.values():
                names.extend([block["name"] for block in category_blocks.values()])
            return names
    
    def combine_prompt_blocks(self, selected_block_ids: List[str], custom_blocks: Dict = None) -> Dict:
        """
        组合提示词块，生成最终的提示词结构
        
        Args:
            selected_block_ids: 选中的提示词块ID列表
            custom_blocks: 自定义提示词块字典
            
        Returns:
            组合后的提示词结构
        """
        combined_prompt = {
            "avoid": [],
            "should": [],
            "custom": {},
            "metadata": {
                "combined_time": datetime.now().isoformat(),
                "selected_blocks": selected_block_ids,
                "total_blocks": len(selected_block_ids)
            }
        }
        
        # 组合选中的提示词块
        for block_id in selected_block_ids:
            block = self.get_block_by_id(block_id)
            if block and "content" in block:
                content = block["content"]
                if "avoid" in content:
                    combined_prompt["avoid"].extend(content["avoid"])
                if "should" in content:
                    combined_prompt["should"].extend(content["should"])
        
        # 添加自定义提示词块
        if custom_blocks:
            combined_prompt["custom"] = custom_blocks
        
        # 去重
        combined_prompt["avoid"] = list(set(combined_prompt["avoid"]))
        combined_prompt["should"] = list(set(combined_prompt["should"]))
        
        return combined_prompt
    
    def generate_final_prompt_json(self, selected_block_ids: List[str], custom_blocks: Dict = None, 
                                 channel_info: Dict = None) -> str:
        """
        生成最终的JSON格式提示词
        
        Args:
            selected_block_ids: 选中的提示词块ID列表
            custom_blocks: 自定义提示词块字典
            channel_info: 频道信息字典
            
        Returns:
            JSON格式的最终提示词字符串
        """
        combined_prompt = self.combine_prompt_blocks(selected_block_ids, custom_blocks)
        
        # 构建最终提示词结构
        final_prompt = {
            "channel_info": channel_info or {},
            "writing_requirements": {
                "avoid": combined_prompt["avoid"],
                "should": combined_prompt["should"]
            },
            "custom_requirements": combined_prompt["custom"],
            "metadata": combined_prompt["metadata"]
        }
        
        return json.dumps(final_prompt, ensure_ascii=False, indent=2)
    
    def get_block_summary(self, block_id: str) -> Dict:
        """获取提示词块摘要信息"""
        block = self.get_block_by_id(block_id)
        if not block:
            return {}
        
        return {
            "id": block.get("id", ""),
            "name": block.get("name", ""),
            "description": block.get("description", ""),
            "category": block.get("category", ""),
            "version": block.get("version", ""),
            "content_summary": {
                "avoid_count": len(block.get("content", {}).get("avoid", [])),
                "should_count": len(block.get("content", {}).get("should", []))
            }
        }
    
    def search_blocks(self, keyword: str) -> List[Dict]:
        """搜索提示词块"""
        results = []
        all_blocks = self.get_all_blocks()
        
        for category, blocks in all_blocks.items():
            for block_id, block in blocks.items():
                if (keyword.lower() in block.get("name", "").lower() or 
                    keyword.lower() in block.get("description", "").lower()):
                    results.append({
                        "id": block_id,
                        "category": category,
                        **block
                    })
        
        return results
    
    def get_blocks_statistics(self) -> Dict:
        """获取提示词块统计信息"""
        all_blocks = self.get_all_blocks()
        stats = {
            "total_blocks": 0,
            "public_blocks": 0,
            "industry_blocks": 0,
            "categories": {}
        }
        
        for category, blocks in all_blocks.items():
            category_count = len(blocks)
            stats["total_blocks"] += category_count
            stats["categories"][category] = category_count
            
            if category == "public":
                stats["public_blocks"] = category_count
            elif category == "industry":
                stats["industry_blocks"] = category_count
        
        return stats
    
    def validate_block_selection(self, selected_block_ids: List[str]) -> Dict:
        """验证提示词块选择的有效性"""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # 检查是否存在冲突的提示词块
        if len(selected_block_ids) == 0:
            validation_result["warnings"].append("未选择任何提示词块")
        
        # 检查提示词块是否存在
        for block_id in selected_block_ids:
            if not self.get_block_by_id(block_id):
                validation_result["errors"].append(f"提示词块 '{block_id}' 不存在")
                validation_result["valid"] = False
        
        # 检查是否有重复选择
        if len(selected_block_ids) != len(set(selected_block_ids)):
            validation_result["warnings"].append("存在重复选择的提示词块")
        
        return validation_result
    
    def create_block(self, block_data: Dict) -> bool:
        """
        创建新的提示词块
        
        Args:
            block_data: 提示词块数据
            
        Returns:
            是否创建成功
        """
        try:
            category = block_data.get("category", "public")
            if category not in ["public", "industry"]:
                category = "public"
            
            # 生成唯一ID
            import uuid
            block_id = str(uuid.uuid4())[:8]
            
            # 确保分类存在
            if "prompt_blocks" not in self.prompt_blocks_data:
                self.prompt_blocks_data["prompt_blocks"] = {}
            if category not in self.prompt_blocks_data["prompt_blocks"]:
                self.prompt_blocks_data["prompt_blocks"][category] = {}
            
            # 添加块数据
            self.prompt_blocks_data["prompt_blocks"][category][block_id] = {
                "id": block_id,
                **block_data
            }
            
            # 更新元数据
            self.prompt_blocks_data["metadata"]["last_modified"] = datetime.now().isoformat()
            
            # 保存到文件
            return self._save_prompt_blocks()
            
        except Exception as e:
            print(f"创建提示词块失败: {e}")
            return False
    
    def update_block(self, block_id: str, updated_data: Dict) -> bool:
        """
        更新提示词块
        
        Args:
            block_id: 提示词块ID
            updated_data: 更新的数据
            
        Returns:
            是否更新成功
        """
        try:
            # 查找块所在位置
            all_blocks = self.get_all_blocks()
            block_found = False
            
            for category, blocks in all_blocks.items():
                if block_id in blocks:
                    # 更新块数据
                    blocks[block_id].update(updated_data)
                    block_found = True
                    break
            
            if not block_found:
                print(f"提示词块 '{block_id}' 不存在")
                return False
            
            # 更新元数据
            self.prompt_blocks_data["metadata"]["last_modified"] = datetime.now().isoformat()
            
            # 保存到文件
            return self._save_prompt_blocks()
            
        except Exception as e:
            print(f"更新提示词块失败: {e}")
            return False
    
    def delete_block(self, block_id: str) -> bool:
        """
        删除提示词块
        
        Args:
            block_id: 提示词块ID
            
        Returns:
            是否删除成功
        """
        try:
            # 查找并删除块
            all_blocks = self.get_all_blocks()
            block_found = False
            
            for category, blocks in all_blocks.items():
                if block_id in blocks:
                    del blocks[block_id]
                    block_found = True
                    break
            
            if not block_found:
                print(f"提示词块 '{block_id}' 不存在")
                return False
            
            # 更新元数据
            self.prompt_blocks_data["metadata"]["last_modified"] = datetime.now().isoformat()
            
            # 保存到文件
            return self._save_prompt_blocks()
            
        except Exception as e:
            print(f"删除提示词块失败: {e}")
            return False
    
    def _save_prompt_blocks(self) -> bool:
        """
        保存提示词块配置到文件
        
        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.prompt_blocks_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"保存提示词块配置失败: {e}")
            return False


# 使用示例
if __name__ == "__main__":
    # 创建提示词块管理器实例
    prompt_manager = PromptBlockManager()
    
    # 获取所有提示词块
    all_blocks = prompt_manager.get_all_blocks()
    print("所有提示词块分类:", list(all_blocks.keys()))
    
    # 获取公共提示词块
    public_blocks = prompt_manager.get_public_blocks()
    print("公共提示词块数量:", len(public_blocks))
    
    # 获取统计信息
    stats = prompt_manager.get_blocks_statistics()
    print("提示词块统计:", stats)
    
    # 测试组合功能
    selected_ids = ["basic_language", "human_editing", "tech"]
    combined = prompt_manager.combine_prompt_blocks(selected_ids)
    print("组合后的提示词结构:", json.dumps(combined, ensure_ascii=False, indent=2))
