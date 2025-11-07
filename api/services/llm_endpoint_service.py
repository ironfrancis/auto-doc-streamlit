"""
LLM 端点业务逻辑服务
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from api.database.models import LLMEndpoint


class LLMEndpointService:
    """LLM 端点服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_endpoints(self) -> List[Dict]:
        """获取所有 LLM 端点"""
        endpoints = self.db.query(LLMEndpoint).all()
        return [self._endpoint_to_dict(ep) for ep in endpoints]
    
    def get_endpoint_by_id(self, endpoint_id: str) -> Optional[Dict]:
        """根据ID获取 LLM 端点"""
        endpoint = self.db.query(LLMEndpoint).filter(LLMEndpoint.id == endpoint_id).first()
        return self._endpoint_to_dict(endpoint) if endpoint else None
    
    def get_default_endpoint(self) -> Optional[Dict]:
        """获取默认 LLM 端点"""
        endpoint = self.db.query(LLMEndpoint).filter(LLMEndpoint.is_default == "true").first()
        return self._endpoint_to_dict(endpoint) if endpoint else None
    
    def create_endpoint(self, endpoint_data: Dict) -> Dict:
        """创建 LLM 端点"""
        # 如果设置为默认，先取消其他默认端点
        if endpoint_data.get("is_default") == "true":
            self.db.query(LLMEndpoint).filter(LLMEndpoint.is_default == "true").update(
                {"is_default": "false"}
            )
        
        endpoint = LLMEndpoint(**endpoint_data)
        self.db.add(endpoint)
        self.db.commit()
        self.db.refresh(endpoint)
        return self._endpoint_to_dict(endpoint)
    
    def update_endpoint(self, endpoint_id: str, endpoint_data: Dict) -> Optional[Dict]:
        """更新 LLM 端点"""
        endpoint = self.db.query(LLMEndpoint).filter(LLMEndpoint.id == endpoint_id).first()
        if not endpoint:
            return None
        
        # 如果设置为默认，先取消其他默认端点
        if endpoint_data.get("is_default") == "true":
            self.db.query(LLMEndpoint).filter(
                LLMEndpoint.id != endpoint_id
            ).filter(LLMEndpoint.is_default == "true").update(
                {"is_default": "false"}
            )
        
        for key, value in endpoint_data.items():
            setattr(endpoint, key, value)
        
        self.db.commit()
        self.db.refresh(endpoint)
        return self._endpoint_to_dict(endpoint)
    
    def delete_endpoint(self, endpoint_id: str) -> bool:
        """删除 LLM 端点"""
        endpoint = self.db.query(LLMEndpoint).filter(LLMEndpoint.id == endpoint_id).first()
        if not endpoint:
            return False
        
        self.db.delete(endpoint)
        self.db.commit()
        return True
    
    def _endpoint_to_dict(self, endpoint: LLMEndpoint) -> Optional[Dict]:
        """将 LLM 端点模型转换为字典"""
        if not endpoint:
            return None
        return {
            "id": endpoint.id,
            "name": endpoint.name,
            "api_type": endpoint.api_type,
            "is_openai_compatible": endpoint.is_openai_compatible,
            "api_url": endpoint.api_url,
            "api_key": endpoint.api_key,
            "model": endpoint.model,
            "temperature": endpoint.temperature,
            "remark": endpoint.remark,
            "is_default": endpoint.is_default,
            "created_at": endpoint.created_at.isoformat() if endpoint.created_at else None,
            "updated_at": endpoint.updated_at.isoformat() if endpoint.updated_at else None,
        }

