"""
频道业务逻辑服务
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from api.database.models import Channel


class ChannelService:
    """频道服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_channels(self) -> List[Dict]:
        """获取所有频道"""
        channels = self.db.query(Channel).all()
        return [self._channel_to_dict(ch) for ch in channels]
    
    def get_channel_by_id(self, channel_id: str) -> Optional[Dict]:
        """根据ID获取频道"""
        channel = self.db.query(Channel).filter(Channel.id == channel_id).first()
        return self._channel_to_dict(channel) if channel else None
    
    def create_channel(self, channel_data: Dict) -> Dict:
        """创建频道"""
        channel = Channel(**channel_data)
        self.db.add(channel)
        self.db.commit()
        self.db.refresh(channel)
        return self._channel_to_dict(channel)
    
    def update_channel(self, channel_id: str, channel_data: Dict) -> Optional[Dict]:
        """更新频道"""
        channel = self.db.query(Channel).filter(Channel.id == channel_id).first()
        if not channel:
            return None
        
        for key, value in channel_data.items():
            setattr(channel, key, value)
        
        self.db.commit()
        self.db.refresh(channel)
        return self._channel_to_dict(channel)
    
    def delete_channel(self, channel_id: str) -> bool:
        """删除频道"""
        channel = self.db.query(Channel).filter(Channel.id == channel_id).first()
        if not channel:
            return False
        
        self.db.delete(channel)
        self.db.commit()
        return True
    
    def _channel_to_dict(self, channel: Channel) -> Dict:
        """将频道模型转换为字典"""
        if not channel:
            return None
        return {
            "id": channel.id,
            "name": channel.name,
            "description": channel.description,
            "template": channel.template,
            "llm_endpoint": channel.llm_endpoint,
            "content_rules": channel.content_rules,
            "created_at": channel.created_at.isoformat() if channel.created_at else None,
            "updated_at": channel.updated_at.isoformat() if channel.updated_at else None,
        }

