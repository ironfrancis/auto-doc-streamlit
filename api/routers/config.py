"""
配置管理 API
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/config")
async def get_config():
    """获取系统配置"""
    # TODO: 实现配置获取逻辑
    return {"message": "配置管理功能待实现"}

