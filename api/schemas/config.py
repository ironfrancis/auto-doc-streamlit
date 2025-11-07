"""
配置相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ImageBedType(str, Enum):
    """图床类型枚举"""
    LSKY = "lsky"
    SCDN = "scdn"
    CUSTOM = "custom"


class InfoSourceType(str, Enum):
    """信息源类型枚举"""
    RSS = "rss"
    WEBSITE = "website"
    API = "api"


# 基础模型
class ImageBedBase(BaseModel):
    """图床基础模型"""
    name: str = Field(..., description="图床名称")
    type: ImageBedType = Field(..., description="图床类型")
    api_url: Optional[str] = Field(None, description="API地址")
    token: Optional[str] = Field(None, description="认证Token")
    is_default: bool = Field(False, description="是否为默认图床")
    is_enabled: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="描述")


class ImageBedCreate(ImageBedBase):
    """创建图床模型"""
    pass


class ImageBedUpdate(BaseModel):
    """更新图床模型"""
    name: Optional[str] = Field(None, description="图床名称")
    type: Optional[ImageBedType] = Field(None, description="图床类型")
    api_url: Optional[str] = Field(None, description="API地址")
    token: Optional[str] = Field(None, description="认证Token")
    is_default: Optional[bool] = Field(None, description="是否为默认图床")
    is_enabled: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="描述")


class ImageBed(ImageBedBase):
    """图床响应模型"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# 微信Token模型
class WechatTokenBase(BaseModel):
    """微信Token基础模型"""
    account_name: str = Field(..., description="公众号名称")
    token: str = Field(..., description="Token")
    status: str = Field("active", description="状态")
    description: Optional[str] = Field(None, description="描述")


class WechatTokenCreate(WechatTokenBase):
    """创建微信Token模型"""
    pass


class WechatTokenUpdate(BaseModel):
    """更新微信Token模型"""
    account_name: Optional[str] = Field(None, description="公众号名称")
    token: Optional[str] = Field(None, description="Token")
    status: Optional[str] = Field(None, description="状态")
    description: Optional[str] = Field(None, description="描述")


class WechatToken(WechatTokenBase):
    """微信Token响应模型"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# 信息源模型
class InfoSourceBase(BaseModel):
    """信息源基础模型"""
    name: str = Field(..., description="信息源名称")
    url: str = Field(..., description="URL地址")
    type: InfoSourceType = Field(..., description="信息源类型")
    config: Optional[Dict[str, Any]] = Field(None, description="额外配置")
    is_enabled: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="描述")


class InfoSourceCreate(InfoSourceBase):
    """创建信息源模型"""
    pass


class InfoSourceUpdate(BaseModel):
    """更新信息源模型"""
    name: Optional[str] = Field(None, description="信息源名称")
    url: Optional[str] = Field(None, description="URL地址")
    type: Optional[InfoSourceType] = Field(None, description="信息源类型")
    config: Optional[Dict[str, Any]] = Field(None, description="额外配置")
    is_enabled: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="描述")


class InfoSource(InfoSourceBase):
    """信息源响应模型"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# 模板模型
class TemplateBase(BaseModel):
    """模板基础模型"""
    name: str = Field(..., description="模板名称")
    file_path: str = Field(..., description="文件路径")
    description: Optional[str] = Field(None, description="描述")
    category: Optional[str] = Field(None, description="分类")
    is_default: bool = Field(False, description="是否为默认模板")


class TemplateCreate(TemplateBase):
    """创建模板模型"""
    pass


class TemplateUpdate(BaseModel):
    """更新模板模型"""
    name: Optional[str] = Field(None, description="模板名称")
    file_path: Optional[str] = Field(None, description="文件路径")
    description: Optional[str] = Field(None, description="描述")
    category: Optional[str] = Field(None, description="分类")
    is_default: Optional[bool] = Field(None, description="是否为默认模板")


class Template(TemplateBase):
    """模板响应模型"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# 通用配置模型
class ConfigBase(BaseModel):
    """配置基础模型"""
    key: str = Field(..., description="配置键")
    value: Dict[str, Any] = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="描述")


class ConfigCreate(ConfigBase):
    """创建配置模型"""
    pass


class ConfigUpdate(BaseModel):
    """更新配置模型"""
    value: Optional[Dict[str, Any]] = Field(None, description="配置值")
    description: Optional[str] = Field(None, description="描述")


class Config(ConfigBase):
    """配置响应模型"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# 批量响应模型
class BatchResponse(BaseModel):
    """批量操作响应"""
    success: int = Field(..., description="成功数量")
    failed: int = Field(..., description="失败数量")
    errors: List[str] = Field([], description="错误信息")