#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cookie管理器
用于管理微信公众号的登录Cookie信息，包括读取、保存、更新和状态检查
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path


class CookieManager:
    """Cookie管理器类"""
    
    def __init__(self, config_file: str = "workspace/data/json/cookies_config.json"):
        """
        初始化Cookie管理器
        
        Args:
            config_file: Cookie配置文件路径
        """
        self.config_file = Path(config_file)
        self.cookies_data = self._load_cookies()
    
    def _load_cookies(self) -> Dict:
        """加载Cookie配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"加载Cookie配置文件失败: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "cookies": {
                "AGI观察室": {
                    "cookie_string": "",
                    "last_updated": None,
                    "status": "inactive",
                    "description": "AGI观察室公众号的登录cookie"
                },
                "AGI启示录": {
                    "cookie_string": "",
                    "last_updated": None,
                    "status": "inactive",
                    "description": "AGI启示录公众号的登录cookie"
                },
                "AI 万象志": {
                    "cookie_string": "",
                    "last_updated": None,
                    "status": "inactive",
                    "description": "AI 万象志公众号的登录cookie"
                },
                "人工智能漫游指南": {
                    "cookie_string": "",
                    "last_updated": None,
                    "status": "inactive",
                    "description": "人工智能漫游指南公众号的登录cookie"
                }
            },
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "description": "微信公众号登录Cookie配置文件",
                "notes": [
                    "Cookie有效期通常为24小时",
                    "建议每12小时更新一次",
                    "如果获取数据失败，请检查Cookie是否过期"
                ]
            }
        }
    
    def _save_cookies(self):
        """保存Cookie配置到文件"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 更新元数据
            self.cookies_data["metadata"]["last_modified"] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.cookies_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存Cookie配置文件失败: {e}")
            return False
    
    def get_cookie(self, account_name: str) -> Optional[str]:
        """
        获取指定公众号的Cookie字符串
        
        Args:
            account_name: 公众号名称
            
        Returns:
            Cookie字符串，如果不存在则返回None
        """
        if account_name in self.cookies_data["cookies"]:
            return self.cookies_data["cookies"][account_name]["cookie_string"]
        return None
    
    def set_cookie(self, account_name: str, cookie_string: str, description: str = "") -> bool:
        """
        设置指定公众号的Cookie
        
        Args:
            account_name: 公众号名称
            cookie_string: Cookie字符串
            description: 描述信息
            
        Returns:
            是否设置成功
        """
        if account_name not in self.cookies_data["cookies"]:
            # 如果是新账号，添加到配置中
            self.cookies_data["cookies"][account_name] = {
                "cookie_string": "",
                "last_updated": None,
                "status": "inactive",
                "description": description or f"{account_name}公众号的登录cookie"
            }
        
        # 更新Cookie信息
        self.cookies_data["cookies"][account_name]["cookie_string"] = cookie_string
        self.cookies_data["cookies"][account_name]["last_updated"] = datetime.now().isoformat()
        self.cookies_data["cookies"][account_name]["status"] = "active"
        
        if description:
            self.cookies_data["cookies"][account_name]["description"] = description
        
        return self._save_cookies()
    
    def remove_cookie(self, account_name: str) -> bool:
        """
        移除指定公众号的Cookie
        
        Args:
            account_name: 公众号名称
            
        Returns:
            是否移除成功
        """
        if account_name in self.cookies_data["cookies"]:
            self.cookies_data["cookies"][account_name]["cookie_string"] = ""
            self.cookies_data["cookies"][account_name]["last_updated"] = None
            self.cookies_data["cookies"][account_name]["status"] = "inactive"
            return self._save_cookies()
        return False
    
    def get_cookie_status(self, account_name: str) -> Dict:
        """
        获取指定公众号的Cookie状态
        
        Args:
            account_name: 公众号名称
            
        Returns:
            包含状态信息的字典
        """
        if account_name not in self.cookies_data["cookies"]:
            return {
                "status": "not_found",
                "message": "公众号未配置",
                "last_updated": None,
                "is_fresh": False,
                "is_expired": True
            }
        
        cookie_info = self.cookies_data["cookies"][account_name]
        last_updated = cookie_info.get("last_updated")
        
        if not cookie_info["cookie_string"]:
            return {
                "status": "inactive",
                "message": "Cookie未配置",
                "last_updated": None,
                "is_fresh": False,
                "is_expired": True
            }
        
        # 如果没有更新时间记录，但有Cookie字符串，则设置为当前时间
        if not last_updated:
            self.cookies_data["cookies"][account_name]["last_updated"] = datetime.now().isoformat()
            self.cookies_data["cookies"][account_name]["status"] = "active"
            self._save_cookies()
            last_updated = self.cookies_data["cookies"][account_name]["last_updated"]
        
        # 确保状态字段与实际情况一致
        if cookie_info["status"] != "active" and cookie_info["cookie_string"]:
            self.cookies_data["cookies"][account_name]["status"] = "active"
            self._save_cookies()
        
        try:
            # 解析时间
            if isinstance(last_updated, str):
                last_update_time = datetime.fromisoformat(last_updated)
            else:
                last_update_time = last_updated
            
            now = datetime.now()
            time_diff = now - last_update_time
            hours_diff = time_diff.total_seconds() / 3600
            
            # 判断状态
            if hours_diff < 2:
                status = "fresh"
                message = "Cookie新鲜"
                is_fresh = True
                is_expired = False
            elif hours_diff < 24:
                status = "warning"
                message = "Cookie建议更新"
                is_fresh = False
                is_expired = False
            else:
                status = "expired"
                message = "Cookie已过期"
                is_fresh = False
                is_expired = True
            
            return {
                "status": status,
                "message": message,
                "last_updated": last_update_time,
                "hours_ago": round(hours_diff, 1),
                "is_fresh": is_fresh,
                "is_expired": is_expired
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"时间解析错误: {e}",
                "last_updated": last_updated,
                "is_fresh": False,
                "is_expired": True
            }
    
    def get_all_cookies(self) -> Dict:
        """获取所有Cookie信息"""
        return self.cookies_data["cookies"]
    
    def get_active_cookies(self) -> Dict:
        """获取所有活跃的Cookie"""
        active_cookies = {}
        for account_name, cookie_info in self.cookies_data["cookies"].items():
            if cookie_info["status"] == "active" and cookie_info["cookie_string"]:
                active_cookies[account_name] = cookie_info
        return active_cookies
    
    def get_expired_cookies(self) -> List[str]:
        """获取所有过期的Cookie账号"""
        expired_accounts = []
        for account_name in self.cookies_data["cookies"]:
            status = self.get_cookie_status(account_name)
            if status["is_expired"]:
                expired_accounts.append(account_name)
        return expired_accounts
    
    def refresh_cookie(self, account_name: str) -> bool:
        """
        刷新指定公众号的Cookie更新时间
        
        Args:
            account_name: 公众号名称
            
        Returns:
            是否刷新成功
        """
        if account_name in self.cookies_data["cookies"]:
            self.cookies_data["cookies"][account_name]["last_updated"] = datetime.now().isoformat()
            return self._save_cookies()
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
        if account_name not in self.cookies_data["cookies"]:
            self.cookies_data["cookies"][account_name] = {
                "cookie_string": "",
                "last_updated": None,
                "status": "inactive",
                "description": description or f"{account_name}公众号的登录cookie"
            }
            return self._save_cookies()
        return False
    
    def get_config_info(self) -> Dict:
        """获取配置文件信息"""
        return {
            "config_file": str(self.config_file),
            "total_accounts": len(self.cookies_data["cookies"]),
            "active_accounts": len(self.get_active_cookies()),
            "expired_accounts": len(self.get_expired_cookies()),
            "metadata": self.cookies_data["metadata"]
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
            backup_file = backup_path / f"cookies_config_backup_{timestamp}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.cookies_data, f, ensure_ascii=False, indent=2)
            
            return str(backup_file)
        except Exception as e:
            print(f"备份配置文件失败: {e}")
            return ""


# 使用示例
if __name__ == "__main__":
    # 创建Cookie管理器实例
    cookie_manager = CookieManager()
    
    # 获取所有Cookie信息
    all_cookies = cookie_manager.get_all_cookies()
    print("所有Cookie账号:", list(all_cookies.keys()))
    
    # 检查AGI观察室的Cookie状态
    status = cookie_manager.get_cookie_status("AGI观察室")
    print("AGI观察室Cookie状态:", status)
    
    # 获取配置文件信息
    config_info = cookie_manager.get_config_info()
    print("配置文件信息:", config_info)

