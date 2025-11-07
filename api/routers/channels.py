"""
频道管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.database.connection import get_db
from api.services.channel_service import ChannelService

router = APIRouter()


@router.get("/channels")
async def get_channels(db: Session = Depends(get_db)):
    """获取所有频道"""
    service = ChannelService(db)
    return service.get_all_channels()


@router.get("/channels/{channel_id}")
async def get_channel(channel_id: str, db: Session = Depends(get_db)):
    """获取单个频道"""
    service = ChannelService(db)
    channel = service.get_channel_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="频道不存在")
    return channel


@router.post("/channels")
async def create_channel(channel_data: dict, db: Session = Depends(get_db)):
    """创建频道"""
    service = ChannelService(db)
    return service.create_channel(channel_data)


@router.put("/channels/{channel_id}")
async def update_channel(
    channel_id: str, channel_data: dict, db: Session = Depends(get_db)
):
    """更新频道"""
    service = ChannelService(db)
    channel = service.update_channel(channel_id, channel_data)
    if not channel:
        raise HTTPException(status_code=404, detail="频道不存在")
    return channel


@router.delete("/channels/{channel_id}")
async def delete_channel(channel_id: str, db: Session = Depends(get_db)):
    """删除频道"""
    service = ChannelService(db)
    success = service.delete_channel(channel_id)
    if not success:
        raise HTTPException(status_code=404, detail="频道不存在")
    return {"message": "频道已删除"}

