"""
LLM 调用 API
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from api.services.llm_service import LLMService
from api.services.llm_endpoint_service import LLMEndpointService
from api.database.connection import get_db
from api.schemas.llm_endpoint import (
    LLMEndpoint,
    LLMEndpointCreate,
    LLMEndpointUpdate
)

router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求模型"""
    endpoint_id: str
    prompt: str
    temperature: float = 0.7
    stream: bool = False


@router.post("/llm/chat")
async def chat(request: ChatRequest):
    """LLM 聊天接口"""
    service = LLMService()
    try:
        result = await service.chat(
            endpoint_id=request.endpoint_id,
            prompt=request.prompt,
            temperature=request.temperature,
            stream=request.stream
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LLM 端点管理 ====================

@router.get("/llm/endpoints", response_model=List[LLMEndpoint])
async def get_llm_endpoints(db: Session = Depends(get_db)):
    """获取所有 LLM 端点"""
    service = LLMEndpointService(db)
    return service.get_all_endpoints()


@router.get("/llm/endpoints/{endpoint_id}", response_model=LLMEndpoint)
async def get_llm_endpoint(endpoint_id: str, db: Session = Depends(get_db)):
    """获取单个 LLM 端点"""
    service = LLMEndpointService(db)
    endpoint = service.get_endpoint_by_id(endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="LLM 端点不存在")
    return endpoint


@router.get("/llm/endpoints/default", response_model=Optional[LLMEndpoint])
async def get_default_llm_endpoint(db: Session = Depends(get_db)):
    """获取默认 LLM 端点"""
    service = LLMEndpointService(db)
    return service.get_default_endpoint()


@router.post("/llm/endpoints", response_model=LLMEndpoint)
async def create_llm_endpoint(
    endpoint: LLMEndpointCreate,
    db: Session = Depends(get_db)
):
    """创建 LLM 端点"""
    service = LLMEndpointService(db)
    return service.create_endpoint(endpoint.dict())


@router.put("/llm/endpoints/{endpoint_id}", response_model=LLMEndpoint)
async def update_llm_endpoint(
    endpoint_id: str,
    endpoint_update: LLMEndpointUpdate,
    db: Session = Depends(get_db)
):
    """更新 LLM 端点"""
    service = LLMEndpointService(db)
    endpoint = service.update_endpoint(endpoint_id, endpoint_update.dict(exclude_unset=True))
    if not endpoint:
        raise HTTPException(status_code=404, detail="LLM 端点不存在")
    return endpoint


@router.delete("/llm/endpoints/{endpoint_id}")
async def delete_llm_endpoint(endpoint_id: str, db: Session = Depends(get_db)):
    """删除 LLM 端点"""
    service = LLMEndpointService(db)
    success = service.delete_endpoint(endpoint_id)
    if not success:
        raise HTTPException(status_code=404, detail="LLM 端点不存在")
    return {"message": "LLM 端点已删除"}

