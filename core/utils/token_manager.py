#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token管理器
用于管理微信公众号的Token信息，包括读取、保存、更新和状态检查
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path


class TokenManager:
    """Token管理器类"""
    
    def __init__(self, config_file: str = "workspace/data/json/tokens_config.json"):
        """
        初始化Token管理器
        
        Args:
            config_file: Token配置文件路径
        """
        self.config_file = Path(config_file)
        self.tokens_data = self._load_tokens()
    
    def _load_tokens(self) -> Dict:
        """加载Token配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"加载Token配置文件失败: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "tokens": {
                "AGI观察室": {
                    "token": "254511315",
                    "last_updated": None,
                    "status": "active",
                    "description": "AGI观察室公众号的token"
                },
                "AGI启示录": {
                    "token": "254511315",
                    "last_updated": None,
                    "status": "active",
                    "description": "AGI启示录公众号的token"
                },
                "AI 万象志": {
                    "token": "254511315",
                    "last_updated": None,
                    "status": "active",
                    "description": "AI 万象志公众号的token"
                },
                "人工智能漫游指南": {
                    "token": "254511315",
                    "last_updated": None,
                    "status": "active",
                    "description": "人工智能漫游指南公众号的token"
                }
            },
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "description": "微信公众号Token配置文件",
                "notes": [
                    "Token用于微信公众平台API调用",
                    "每个公众号都有唯一的token",
                    "如果token失效，请联系管理员更新"
                ]
            }
        }
    
    def _save_tokens(self):
        """保存Token配置到文件"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 更新元数据
            self.tokens_data["metadata"]["last_modified"] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.tokens_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存Token配置文件失败: {e}")
            return False
    
    def get_token(self, account_name: str) -> Optional[str]:
        """
        获取指定公众号的Token
        
        Args:
            account_name: 公众号名称
            
        Returns:
            Token字符串，如果不存在则返回None
        """
        if account_name in self.tokens_data["tokens"]:
            return self.tokens_data["tokens"][account_name]["token"]
        return None
    
    def set_token(self, account_name: str, token: str, description: str = "") -> bool:
        """
        设置指定公众号的Token
        
        Args:
            account_name: 公众号名称
            token: Token字符串
            description: 描述信息
            
        Returns:
            是否设置成功
        """
        if account_name not in self.tokens_data["tokens"]:
            # 如果是新账号，添加到配置中
            self.tokens_data["tokens"][account_name] = {
                "token": "",
                "last_updated": None,
                "status": "active",
                "description": description or f"{account_name}公众号的token"
            }
        
        # 更新Token信息
        self.tokens_data["tokens"][account_name]["token"] = token
        self.tokens_data["tokens"][account_name]["last_updated"] = datetime.now().isoformat()
        self.tokens_data["tokens"][account_name]["status"] = "active"
        
        if description:
            self.tokens_data["tokens"][account_name]["description"] = description
        
        return self._save_tokens()
    
    def remove_token(self, account_name: str) -> bool:
        """
        移除指定公众号的Token
        
        Args:
            account_name: 公众号名称
            
        Returns:
            是否移除成功
        """
        if account_name in self.tokens_data["tokens"]:
            self.tokens_data["tokens"][account_name]["token"] = ""
            self.tokens_data["tokens"][account_name]["last_updated"] = None
            self.tokens_data["tokens"][account_name]["status"] = "inactive"
            return self._save_tokens()
        return False
    
    def get_token_status(self, account_name: str) -> Dict:
        """
        获取指定公众号的Token状态
        
        Args:
            account_name: 公众号名称
            
        Returns:
            包含状态信息的字典
        """
        if account_name not in self.tokens_data["tokens"]:
            return {
                "status": "not_found",
                "message": "公众号未配置",
                "last_updated": None,
                "is_active": False
            }
        
        token_info = self.tokens_data["tokens"][account_name]
        last_updated = token_info.get("last_updated")
        
        if not token_info["token"]:
            return {
                "status": "inactive",
                "message": "Token未配置",
                "last_updated": None,
                "is_active": False
            }
        
        # 如果没有更新时间记录，但有Token字符串，则设置为当前时间
        if not last_updated:
            self.tokens_data["tokens"][account_name]["last_updated"] = datetime.now().isoformat()
            self._save_tokens()
            last_updated = self.tokens_data["tokens"][account_name]["last_updated"]
        
        return {
            "status": "active",
            "message": "Token已配置",
            "last_updated": last_updated,
            "is_active": True
        }
    
    def get_all_tokens(self) -> Dict:
        """获取所有Token信息"""
        return self.tokens_data["tokens"]
    
    def get_active_tokens(self) -> Dict:
        """获取所有活跃的Token"""
        active_tokens = {}
        for account_name, token_info in self.tokens_data["tokens"].items():
            if token_info["status"] == "active" and token_info["token"]:
                active_tokens[account_name] = token_info
        return active_tokens
    
    def refresh_token(self, account_name: str) -> bool:
        """
        刷新指定公众号的Token更新时间
        
        Args:
            account_name: 公众号名称
            
        Returns:
            是否刷新成功
        """
        if account_name in self.tokens_data["tokens"]:
            self.tokens_data["tokens"][account_name]["last_updated"] = datetime.now().isoformat()
            return self._save_tokens()
        return False
    
    def add_custom_account(self, account_name: str, description: str = "") -> bool:
        """
        添加自定义公众号账号
        
        Args:
            account_name: 公众号名称
            description: 描述信息
            
        Returns:
            是否添加成功
        """
        if account_name not in self.tokens_data["tokens"]:
            self.tokens_data["tokens"][account_name] = {
                "token": "",
                "last_updated": None,
                "status": "inactive",
                "description": description or f"{account_name}公众号的token"
            }
            return self._save_tokens()
        return False
    
    def get_config_info(self) -> Dict:
        """获取配置文件信息"""
        return {
            "config_file": str(self.config_file),
            "total_accounts": len(self.tokens_data["tokens"]),
            "active_accounts": len(self.get_active_tokens()),
            "metadata": self.tokens_data["metadata"]
        }
    
    def backup_config(self, backup_dir: str = "backups") -> str:
        """
        备份配置文件
        
        Args:
            backup_dir: 备份目录
            
        Returns:
            备份文件路径
        """
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_path / f"tokens_config_backup_{timestamp}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.tokens_data, f, ensure_ascii=False, indent=2)
            
            return str(backup_file)
        except Exception as e:
            print(f"备份配置文件失败: {e}")
            return ""


# 使用示例
if __name__ == "__main__":
    # 创建Token管理器实例
    token_manager = TokenManager()
    
    # 获取所有Token信息
    all_tokens = token_manager.get_all_tokens()
    print("所有Token账号:", list(all_tokens.keys()))
    
    # 检查AGI观察室的Token状态
    status = token_manager.get_token_status("AGI观察室")
    print("AGI观察室Token状态:", status)
    
    # 获取配置文件信息
    config_info = token_manager.get_config_info()
    print("配置文件信息:", config_info)
