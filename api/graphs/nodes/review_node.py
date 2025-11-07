"""
审核节点
"""
from typing import Dict, Any
from api.graphs.state import WorkflowState
from api.services.llm_service import LLMService


async def review_node(state: WorkflowState) -> Dict[str, Any]:
    """内容审核节点"""
    llm_service = LLMService()
    
    draft = state.get('draft', '')
    if not draft:
        return {
            "errors": state.get("errors", []) + ["没有可审核的内容"],
            "current_step": "review_failed"
        }
    
    # 构建审核提示词
    review_prompt = f"""
    请审核以下内容，评估其质量、准确性、语言表达和风格一致性。
    给出评分（0-100）和具体的改进建议。
    
    内容：
    {draft}
    
    请以 JSON 格式返回：
    {{
        "score": 85,
        "issues": ["问题1", "问题2"],
        "suggestions": ["建议1", "建议2"]
    }}
    """
    
    # 调用审核模型
    result = await llm_service.chat(
        endpoint_id=state.get('review_model', ''),
        prompt=review_prompt,
        temperature=0.3
    )
    
    # 解析审核结果
    import json
    try:
        review_data = json.loads(result.get("content", "{}"))
    except:
        review_data = {"score": 0, "issues": [], "suggestions": []}
    
    score = review_data.get("score", 0)
    needs_optimization = score < 70
    
    return {
        "review_results": review_data,
        "quality_score": score,
        "needs_optimization": needs_optimization,
        "current_step": "review_completed",
        "metadata": {
            **state.get("metadata", {}),
            "review_score": score
        }
    }

