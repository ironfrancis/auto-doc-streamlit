#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量配置管理器
用于管理环境变量和配置文件的加载，支持.env文件和环境变量覆盖
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class EnvConfig:
    """环境变量配置管理器类"""
    
    def __init__(self, env_file: str = ".env"):
        """
        初始化环境变量配置管理器
        
        Args:
            env_file: .env文件路径
        """
        self.env_file = Path(env_file)
        self.config = {}
        self._load_env()
        self._load_config()
    
    def _load_env(self):
        """加载.env文件"""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            print(f"✅ 已加载环境变量文件: {self.env_file}")
        else:
            print(f"⚠️  环境变量文件不存在: {self.env_file}")
            print("💡 请复制 .env.example 为 .env 并填入您的配置")
    
    def _load_config(self):
        """加载配置到内存"""
        self.config = {
            # 项目路径配置
            'PROJECT_ROOT': os.getenv('PROJECT_ROOT', '.'),
            'APP_DIR': os.getenv('APP_DIR', 'app'),
            'CONFIG_DIR': os.getenv('CONFIG_DIR', 'config'),
            'TEMPLATES_DIR': os.getenv('TEMPLATES_DIR', 'templates'),
            'STATIC_DIR': os.getenv('STATIC_DIR', 'static'),
            'WORKSPACE_DIR': os.getenv('WORKSPACE_DIR', 'workspace'),
            
            # 数据目录
            'MD_REVIEW_DIR': os.getenv('MD_REVIEW_DIR', 'workspace/articles/md_review'),
            'IMAGES_DIR': os.getenv('IMAGES_DIR', 'workspace/images'),
            'EXPORTS_DIR': os.getenv('EXPORTS_DIR', 'workspace/exports'),
            'ARTICLES_DIR': os.getenv('ARTICLES_DIR', 'workspace/articles'),
            
            # LLM API配置
            'DEFAULT_LLM_API_URL': os.getenv('DEFAULT_LLM_API_URL', 'https://api.openai.com/v1/chat/completions'),
            'DEFAULT_LLM_API_KEY': os.getenv('DEFAULT_LLM_API_KEY', ''),
            'DEFAULT_LLM_MODEL': os.getenv('DEFAULT_LLM_MODEL', 'gpt-3.5-turbo'),
            'DEFAULT_LLM_TEMPERATURE': float(os.getenv('DEFAULT_LLM_TEMPERATURE', '0.7')),
            
            # 备用LLM配置
            'BACKUP_LLM_API_URL': os.getenv('BACKUP_LLM_API_URL', ''),
            'BACKUP_LLM_API_KEY': os.getenv('BACKUP_LLM_API_KEY', ''),
            'BACKUP_LLM_MODEL': os.getenv('BACKUP_LLM_MODEL', ''),
            
            # 微信公众号配置
            'WECHAT_TOKENS': self._parse_json_env('WECHAT_TOKENS', {}),
            'WECHAT_COOKIES': self._parse_json_env('WECHAT_COOKIES', {}),
            
            # 第三方服务配置
            'IMAGE_SERVICE_URL': os.getenv('IMAGE_SERVICE_URL', ''),
            'IMAGE_SERVICE_KEY': os.getenv('IMAGE_SERVICE_KEY', ''),
            'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///workspace/data/app.db'),
            'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379'),
            
            # 安全配置
            'SECRET_KEY': os.getenv('SECRET_KEY', 'default_secret_key_change_in_production'),
            'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_change_in_production'),
            
            # 日志配置
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'LOG_FILE': os.getenv('LOG_FILE', 'workspace/logs/app.log'),
            
            # 其他配置
            'MAX_UPLOAD_SIZE': int(os.getenv('MAX_UPLOAD_SIZE', '100')),
            'SESSION_TIMEOUT': int(os.getenv('SESSION_TIMEOUT', '60')),
            'DEBUG_MODE': os.getenv('DEBUG_MODE', 'False').lower() == 'true',
            'DEBUG': os.getenv('DEBUG', 'True').lower() == 'true'
        }
    
    def _parse_json_env(self, key: str, default: Any) -> Any:
        """解析JSON格式的环境变量"""
        value = os.getenv(key, '')
        if not value:
            return default
        
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            print(f"⚠️  环境变量 {key} 的JSON格式无效，使用默认值")
            return default
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def get_path(self, key: str) -> Path:
        """
        获取路径配置，返回Path对象
        
        Args:
            key: 配置键
            
        Returns:
            Path对象
        """
        path_str = self.get(key, '')
        return Path(path_str)
    
    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        return {
            'api_url': self.get('DEFAULT_LLM_API_URL'),
            'api_key': self.get('DEFAULT_LLM_API_KEY'),
            'model': self.get('DEFAULT_LLM_MODEL'),
            'temperature': self.get('DEFAULT_LLM_TEMPERATURE')
        }
    
    def get_backup_llm_config(self) -> Dict[str, Any]:
        """获取备用LLM配置"""
        return {
            'api_url': self.get('BACKUP_LLM_API_URL'),
            'api_key': self.get('BACKUP_LLM_API_KEY'),
            'model': self.get('BACKUP_LLM_MODEL'),
            'temperature': self.get('DEFAULT_LLM_TEMPERATURE')
        }
    
    def get_wechat_tokens(self) -> Dict[str, str]:
        """获取微信公众号Token配置"""
        return self.get('WECHAT_TOKENS', {})
    
    def get_wechat_cookies(self) -> Dict[str, str]:
        """获取微信公众号Cookie配置"""
        return self.get('WECHAT_COOKIES', {})
    
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return not self.get('DEBUG', True)
    
    def validate_required_config(self) -> bool:
        """验证必需的配置是否存在"""
        required_configs = [
            'DEFAULT_LLM_API_KEY',
            'SECRET_KEY'
        ]
        
        missing_configs = []
        for config in required_configs:
            if not self.get(config) or self.get(config) in ['', 'your_api_key_here', 'your_secret_key_here']:
                missing_configs.append(config)
        
        if missing_configs:
            print("❌ 缺少必需的配置:")
            for config in missing_configs:
                print(f"   - {config}")
            print("💡 请在 .env 文件中配置这些值")
            return False
        
        return True
    
    def print_config_summary(self):
        """打印配置摘要"""
        print("📋 当前配置摘要:")
        print(f"   项目根目录: {self.get('PROJECT_ROOT')}")
        print(f"   调试模式: {'开启' if self.get('DEBUG') else '关闭'}")
        print(f"   LLM API: {self.get('DEFAULT_LLM_MODEL')}")
        print(f"   微信公众号数量: {len(self.get_wechat_tokens())}")
        print(f"   配置验证: {'通过' if self.validate_required_config() else '失败'}")


# 全局配置实例
config = EnvConfig()


def get_config() -> EnvConfig:
    """获取全局配置实例"""
    return config


def reload_config():
    """重新加载配置"""
    global config
    config = EnvConfig()
    return config
