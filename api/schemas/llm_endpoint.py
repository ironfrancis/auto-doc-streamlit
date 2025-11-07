"""
LLM 端点相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LLMEndpointBase(BaseModel):
    """LLM 端点基础模型"""
    name: str = Field(..., description="端点名称")
    api_type: str = Field(..., description="API类型 (OpenAI, Magic, Qwen, Claude, Other)")
    is_openai_compatible: str = Field("false", description="是否兼容 OpenAI API")
    api_url: str = Field(..., description="API地址")
    api_key: Optional[str] = Field(None, description="API密钥")
    model: Optional[str] = Field(None, description="模型名称")
    temperature: str = Field("0.7", description="温度参数")
    remark: Optional[str] = Field(None, description="备注")
    is_default: str = Field("false", description="是否为默认端点")


class LLMEndpointCreate(LLMEndpointBase):
    """创建 LLM 端点模型"""
    pass


class LLMEndpointUpdate(BaseModel):
    """更新 LLM 端点模型"""
    name: Optional[str] = Field(None, description="端点名称")
    api_type: Optional[str] = Field(None, description="API类型")
    is_openai_compatible: Optional[str] = Field(None, description="是否兼容 OpenAI API")
    api_url: Optional[str] = Field(None, description="API地址")
    api_key: Optional[str] = Field(None, description="API密钥")
    model: Optional[str] = Field(None, description="模型名称")
    temperature: Optional[str] = Field(None, description="温度参数")
    remark: Optional[str] = Field(None, description="备注")
    is_default: Optional[str] = Field(None, description="是否为默认端点")


class LLMEndpoint(LLMEndpointBase):
    """LLM 端点响应模型"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

