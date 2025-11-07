"""
LLM 调用 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.services.llm_service import LLMService

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

