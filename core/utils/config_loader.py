#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载器
统一管理所有配置文件的加载，支持环境变量覆盖
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from .env_config import get_config


class ConfigLoader:
    """配置加载器类"""
    
    def __init__(self):
        """初始化配置加载器"""
        self.env_config = get_config()
        self.config_dir = self.env_config.get_path('CONFIG_DIR')
    
    def load_llm_endpoints(self) -> List[Dict[str, Any]]:
        """
        加载LLM端点配置
        
        Returns:
            LLM端点配置列表
        """
        config_file = self.config_dir / "llm_endpoints.json"
        example_file = self.config_dir / "llm_endpoints.example.json"
        
        # 如果配置文件不存在，使用示例文件
        if not config_file.exists() and example_file.exists():
            print(f"⚠️  LLM端点配置文件不存在，使用示例配置: {example_file}")
            config_file = example_file
        
        if not config_file.exists():
            print("❌ LLM端点配置文件不存在，请创建配置文件")
            return []
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                endpoints = json.load(f)
            
            # 使用环境变量覆盖默认配置
            for endpoint in endpoints:
                if endpoint.get('name') == 'OpenAI GPT-3.5 Turbo':
                    if self.env_config.get('DEFAULT_LLM_API_KEY'):
                        endpoint['api_key'] = self.env_config.get('DEFAULT_LLM_API_KEY')
                    if self.env_config.get('DEFAULT_LLM_API_URL'):
                        endpoint['api_url'] = self.env_config.get('DEFAULT_LLM_API_URL')
                    if self.env_config.get('DEFAULT_LLM_MODEL'):
                        endpoint['model'] = self.env_config.get('DEFAULT_LLM_MODEL')
            
            return endpoints
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ 加载LLM端点配置失败: {e}")
            return []
    
    def load_channels(self) -> Dict[str, Any]:
        """
        加载频道配置
        
        Returns:
            频道配置字典
        """
        config_file = self.config_dir / "channels_v3.json"
        example_file = self.config_dir / "channels_v3.example.json"
        
        # 如果配置文件不存在，使用示例文件
        if not config_file.exists() and example_file.exists():
            print(f"⚠️  频道配置文件不存在，使用示例配置: {example_file}")
            config_file = example_file
        
        if not config_file.exists():
            print("❌ 频道配置文件不存在，请创建配置文件")
            return {"channels": []}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ 加载频道配置失败: {e}")
            return {"channels": []}
    
    def load_wechat_tokens(self) -> Dict[str, Any]:
        """
        加载微信公众号Token配置
        
        Returns:
            Token配置字典
        """
        # 优先使用环境变量
        env_tokens = self.env_config.get_wechat_tokens()
        if env_tokens:
            return {
                "tokens": env_tokens,
                "metadata": {
                    "version": "1.0",
                    "source": "environment_variables",
                    "description": "从环境变量加载的Token配置"
                }
            }
        
        # 回退到配置文件
        config_file = self.config_dir / "tokens_config.json"
        example_file = self.config_dir / "tokens_config.example.json"
        
        if not config_file.exists() and example_file.exists():
            print(f"⚠️  Token配置文件不存在，使用示例配置: {example_file}")
            config_file = example_file
        
        if not config_file.exists():
            print("❌ Token配置文件不存在，请创建配置文件")
            return {"tokens": {}}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ 加载Token配置失败: {e}")
            return {"tokens": {}}
    
    def load_wechat_cookies(self) -> Dict[str, Any]:
        """
        加载微信公众号Cookie配置
        
        Returns:
            Cookie配置字典
        """
        # 优先使用环境变量
        env_cookies = self.env_config.get_wechat_cookies()
        if env_cookies:
            return {
                "cookies": env_cookies,
                "metadata": {
                    "version": "1.0",
                    "source": "environment_variables",
                    "description": "从环境变量加载的Cookie配置"
                }
            }
        
        # 回退到配置文件
        config_file = self.config_dir / "cookies_config.json"
        example_file = self.config_dir / "cookies_config.example.json"
        
        if not config_file.exists() and example_file.exists():
            print(f"⚠️  Cookie配置文件不存在，使用示例配置: {example_file}")
            config_file = example_file
        
        if not config_file.exists():
            print("❌ Cookie配置文件不存在，请创建配置文件")
            return {"cookies": {}}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ 加载Cookie配置失败: {e}")
            return {"cookies": {}}
    
    def load_template_info(self) -> Dict[str, Any]:
        """
        加载模板信息配置
        
        Returns:
            模板信息配置字典
        """
        config_file = self.config_dir / "template_info.json"
        
        if not config_file.exists():
            print("❌ 模板信息配置文件不存在")
            return {"templates": []}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ 加载模板信息配置失败: {e}")
            return {"templates": []}
    
    def load_info_sources(self) -> Dict[str, Any]:
        """
        加载信息源配置
        
        Returns:
            信息源配置字典
        """
        config_file = self.config_dir / "info_sources.json"
        
        if not config_file.exists():
            print("❌ 信息源配置文件不存在")
            return {"sources": []}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ 加载信息源配置失败: {e}")
            return {"sources": []}
    
    def get_config_path(self, config_name: str) -> Path:
        """
        获取配置文件路径
        
        Args:
            config_name: 配置文件名
            
        Returns:
            配置文件路径
        """
        return self.config_dir / config_name
    
    def create_example_configs(self):
        """创建示例配置文件"""
        example_files = [
            "llm_endpoints.example.json",
            "tokens_config.example.json", 
            "cookies_config.example.json",
            "channels_v3.example.json"
        ]
        
        for file_name in example_files:
            example_file = self.config_dir / file_name
            if example_file.exists():
                print(f"✅ 示例配置文件已存在: {example_file}")
            else:
                print(f"❌ 示例配置文件不存在: {example_file}")


# 全局配置加载器实例
config_loader = ConfigLoader()


def get_config_loader() -> ConfigLoader:
    """获取全局配置加载器实例"""
    return config_loader
