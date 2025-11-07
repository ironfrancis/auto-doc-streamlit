"""
内容生成节点
"""
from typing import Dict, Any
from api.graphs.state import WorkflowState
from api.services.llm_service import LLMService


async def generation_node(state: WorkflowState) -> Dict[str, Any]:
    """内容生成节点"""
    llm_service = LLMService()
    
    # 构建提示词
    prompt = f"""
    请根据以下要求生成内容：
    
    频道配置：
    {state.get('channel_config', {})}
    
    用户输入：
    {state.get('input_content', '')}
    
    请生成高质量的内容。
    """
    
    # 调用 LLM
    result = await llm_service.chat(
        endpoint_id=state.get('llm_endpoint', ''),
        prompt=prompt,
        temperature=0.7
    )
    
    # 更新状态
    return {
        "draft": result.get("content", ""),
        "current_step": "generation_completed",
        "metadata": {
            **state.get("metadata", {}),
            "generation_time": result.get("elapsed_time", 0),
            "generation_model": state.get('llm_endpoint', '')
        }
    }

