#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的 API 客户端
封装所有 FastAPI 后端调用，提供统一的接口和错误处理
"""

import os
import requests
from typing import Dict, List, Optional, Any
from functools import wraps


def get_api_base_url() -> str:
    """获取 API 基础 URL"""
    # 从环境变量获取，支持 Docker 和本地环境
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    # 确保 URL 格式正确
    api_base_url = api_base_url.rstrip("/")
    # 如果 URL 不包含 /api/v1，则添加
    if not api_base_url.endswith("/api/v1"):
        # 检查是否已经包含 /api
        if "/api" not in api_base_url:
            api_base_url = f"{api_base_url}/api/v1"
        elif not api_base_url.endswith("/v1"):
            api_base_url = f"{api_base_url}/v1"
    return api_base_url


def handle_api_error(func):
    """API 调用错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise APIConnectionError(f"无法连接到 API 服务器: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise APITimeoutError(f"API 请求超时: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"API 请求失败: {str(e)}")
    return wrapper


class APIError(Exception):
    """API 调用基础异常"""
    pass


class APIConnectionError(APIError):
    """API 连接错误"""
    pass


class APITimeoutError(APIError):
    """API 超时错误"""
    pass


class APIClient:
    """统一的 API 客户端"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        初始化 API 客户端
        
        Args:
            base_url: API 基础 URL，如果为 None 则从环境变量获取
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url or get_api_base_url()
        self.timeout = timeout
        self.session = requests.Session()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        发送 HTTP 请求
        
        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE)
            endpoint: API 端点路径（不包含 /api/v1 前缀）
            json_data: JSON 请求体
            params: URL 查询参数
            **kwargs: 其他请求参数
            
        Returns:
            响应 JSON 数据
            
        Raises:
            APIError: API 调用失败
        """
        # 构建完整 URL
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        url = f"{self.base_url}/{endpoint}"
        
        # 发送请求
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                timeout=self.timeout,
                **kwargs
            )
            
            # 检查响应状态
            if response.status_code >= 400:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json().get("detail", response.text)
                    error_msg = f"{error_msg}: {error_detail}"
                except:
                    error_msg = f"{error_msg}: {response.text[:200]}"
                raise APIError(error_msg)
            
            # 返回 JSON 数据
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.ConnectionError as e:
            raise APIConnectionError(f"无法连接到 API 服务器 ({url}): {str(e)}")
        except requests.exceptions.Timeout as e:
            raise APITimeoutError(f"API 请求超时 ({url}): {str(e)}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"API 请求失败 ({url}): {str(e)}")
    
    # ==================== 频道管理 ====================
    
    @handle_api_error
    def get_channels(self) -> List[Dict]:
        """获取所有频道"""
        return self._make_request("GET", "channels")
    
    @handle_api_error
    def get_channel(self, channel_id: str) -> Dict:
        """获取单个频道"""
        return self._make_request("GET", f"channels/{channel_id}")
    
    @handle_api_error
    def create_channel(self, channel_data: Dict) -> Dict:
        """创建频道"""
        return self._make_request("POST", "channels", json_data=channel_data)
    
    @handle_api_error
    def update_channel(self, channel_id: str, channel_data: Dict) -> Dict:
        """更新频道"""
        return self._make_request("PUT", f"channels/{channel_id}", json_data=channel_data)
    
    @handle_api_error
    def delete_channel(self, channel_id: str) -> Dict:
        """删除频道"""
        return self._make_request("DELETE", f"channels/{channel_id}")
    
    # ==================== LLM 端点管理 ====================
    
    @handle_api_error
    def get_llm_endpoints(self) -> List[Dict]:
        """获取所有 LLM 端点"""
        return self._make_request("GET", "llm/endpoints")
    
    @handle_api_error
    def get_llm_endpoint(self, endpoint_id: str) -> Dict:
        """获取单个 LLM 端点"""
        return self._make_request("GET", f"llm/endpoints/{endpoint_id}")
    
    @handle_api_error
    def get_default_llm_endpoint(self) -> Optional[Dict]:
        """获取默认 LLM 端点"""
        return self._make_request("GET", "llm/endpoints/default")
    
    @handle_api_error
    def create_llm_endpoint(self, endpoint_data: Dict) -> Dict:
        """创建 LLM 端点"""
        return self._make_request("POST", "llm/endpoints", json_data=endpoint_data)
    
    @handle_api_error
    def update_llm_endpoint(self, endpoint_id: str, endpoint_data: Dict) -> Dict:
        """更新 LLM 端点"""
        return self._make_request("PUT", f"llm/endpoints/{endpoint_id}", json_data=endpoint_data)
    
    @handle_api_error
    def delete_llm_endpoint(self, endpoint_id: str) -> Dict:
        """删除 LLM 端点"""
        return self._make_request("DELETE", f"llm/endpoints/{endpoint_id}")
    
    # ==================== 图床管理 ====================
    
    @handle_api_error
    def get_image_beds(self, enabled_only: bool = False) -> List[Dict]:
        """获取图床列表"""
        params = {"enabled_only": enabled_only} if enabled_only else None
        return self._make_request("GET", "config/image-beds", params=params)
    
    @handle_api_error
    def get_default_image_bed(self) -> Optional[Dict]:
        """获取默认图床"""
        return self._make_request("GET", "config/image-beds/default")
    
    @handle_api_error
    def create_image_bed(self, bed_data: Dict) -> Dict:
        """创建图床配置"""
        return self._make_request("POST", "config/image-beds", json_data=bed_data)
    
    @handle_api_error
    def update_image_bed(self, bed_id: str, bed_data: Dict) -> Dict:
        """更新图床配置"""
        return self._make_request("PUT", f"config/image-beds/{bed_id}", json_data=bed_data)
    
    @handle_api_error
    def delete_image_bed(self, bed_id: str) -> Dict:
        """删除图床配置"""
        return self._make_request("DELETE", f"config/image-beds/{bed_id}")
    
    # ==================== 文章管理 ====================
    
    @handle_api_error
    def get_articles(self, skip: int = 0, limit: int = 100, channel_id: Optional[str] = None) -> List[Dict]:
        """获取文章列表"""
        params = {"skip": skip, "limit": limit}
        if channel_id:
            params["channel_id"] = channel_id
        return self._make_request("GET", "articles", params=params)
    
    @handle_api_error
    def get_article(self, article_id: str) -> Dict:
        """获取单个文章"""
        return self._make_request("GET", f"articles/{article_id}")
    
    @handle_api_error
    def create_article(self, article_data: Dict) -> Dict:
        """创建文章"""
        return self._make_request("POST", "articles", json_data=article_data)
    
    @handle_api_error
    def update_article(self, article_id: str, article_data: Dict) -> Dict:
        """更新文章"""
        return self._make_request("PUT", f"articles/{article_id}", json_data=article_data)
    
    @handle_api_error
    def delete_article(self, article_id: str) -> Dict:
        """删除文章"""
        return self._make_request("DELETE", f"articles/{article_id}")
    
    # ==================== 工作流管理 ====================
    
    @handle_api_error
    def start_content_creation_workflow(self, workflow_data: Dict) -> Dict:
        """启动内容创作工作流"""
        return self._make_request("POST", "workflows/content-creation", json_data=workflow_data)
    
    @handle_api_error
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """获取工作流状态"""
        return self._make_request("GET", f"workflows/{workflow_id}")
    
    # ==================== LLM 聊天 ====================
    
    @handle_api_error
    def chat(self, endpoint_id: str, prompt: str, temperature: float = 0.7, stream: bool = False) -> Dict:
        """LLM 聊天接口"""
        data = {
            "endpoint_id": endpoint_id,
            "prompt": prompt,
            "temperature": temperature,
            "stream": stream
        }
        return self._make_request("POST", "llm/chat", json_data=data)
    
    # ==================== 数据格式转换工具 ====================
    
    @staticmethod
    def convert_channel_to_legacy_format(channel: Dict) -> Dict:
        """将 API 返回的频道格式转换为页面期望的格式"""
        return {
            "id": channel.get("id", ""),
            "name": channel.get("name", ""),
            "description": channel.get("description", ""),
            "template": channel.get("template", ""),
            "llm_endpoint": channel.get("llm_endpoint", ""),
            "content_rules": channel.get("content_rules", {})
        }
    
    @staticmethod
    def convert_llm_endpoint_to_legacy_format(endpoint: Dict) -> Dict:
        """将 API 返回的 LLM 端点格式转换为页面期望的格式"""
        # 安全处理 temperature 字段
        temp_value = endpoint.get("temperature", "0.7")
        if temp_value is None or temp_value == "None" or temp_value == "":
            temp_value = 0.7
        elif isinstance(temp_value, str):
            try:
                temp_value = float(temp_value)
            except (ValueError, TypeError):
                temp_value = 0.7
        else:
            try:
                temp_value = float(temp_value)
            except (ValueError, TypeError):
                temp_value = 0.7
        
        return {
            "id": endpoint.get("id", ""),  # 保留 ID 用于更新和删除
            "name": endpoint.get("name", ""),
            "api_type": endpoint.get("api_type", ""),
            "is_openai_compatible": endpoint.get("is_openai_compatible", "false") == "true",
            "api_url": endpoint.get("api_url", ""),
            "api_key": endpoint.get("api_key", ""),
            "model": endpoint.get("model", ""),
            "temperature": temp_value,
            "remark": endpoint.get("remark", ""),
            "default": endpoint.get("is_default", "false") == "true"
        }
    
    @staticmethod
    def convert_image_bed_to_legacy_format(bed: Dict) -> Dict:
        """将 API 返回的图床格式转换为页面期望的格式"""
        return {
            "id": bed.get("id", ""),
            "name": bed.get("name", ""),
            "type": bed.get("bed_type", bed.get("type", "")),  # 兼容两种字段名
            "api_url": bed.get("api_url", ""),
            "token": bed.get("auth_token", bed.get("token", "")),  # 兼容两种字段名
            "description": bed.get("description", ""),
            "enabled": bed.get("is_enabled", "true") == "true",
            "default": bed.get("is_default", "false") == "true"
        }
    
    @staticmethod
    def convert_llm_endpoint_to_api_format(endpoint: Dict) -> Dict:
        """将页面格式的 LLM 端点转换为 API 格式"""
        # 安全处理 temperature 字段
        temp_value = endpoint.get("temperature", 0.7)
        if temp_value is None or temp_value == "None" or temp_value == "":
            temp_value = "0.7"
        else:
            try:
                temp_value = str(float(temp_value))
            except (ValueError, TypeError):
                temp_value = "0.7"
        
        return {
            "name": endpoint.get("name", ""),
            "api_type": endpoint.get("api_type", ""),
            "is_openai_compatible": "true" if endpoint.get("is_openai_compatible", False) else "false",
            "api_url": endpoint.get("api_url", ""),
            "api_key": endpoint.get("api_key", ""),
            "model": endpoint.get("model", ""),
            "temperature": temp_value,
            "remark": endpoint.get("remark", ""),
            "is_default": "true" if endpoint.get("default", False) else "false"
        }
    
    @staticmethod
    def convert_image_bed_to_api_format(bed: Dict) -> Dict:
        """将页面格式的图床转换为 API 格式"""
        return {
            "name": bed.get("name", ""),
            "bed_type": bed.get("type", bed.get("bed_type", "")),
            "api_url": bed.get("api_url", ""),
            "auth_token": bed.get("token", bed.get("auth_token", "")),
            "description": bed.get("description", ""),
            "is_enabled": "true" if bed.get("enabled", True) else "false",
            "is_default": "true" if bed.get("default", False) else "false"
        }


# 创建全局客户端实例
_default_client: Optional[APIClient] = None


def get_api_client(base_url: Optional[str] = None) -> APIClient:
    """获取 API 客户端实例（单例模式）"""
    global _default_client
    if _default_client is None:
        _default_client = APIClient(base_url=base_url)
    return _default_client


def reset_api_client():
    """重置 API 客户端实例（用于测试）"""
    global _default_client
    _default_client = None

