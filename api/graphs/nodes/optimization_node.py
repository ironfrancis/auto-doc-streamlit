"""
优化节点
"""
from typing import Dict, Any
from api.graphs.state import WorkflowState
from api.services.llm_service import LLMService


async def optimization_node(state: WorkflowState) -> Dict[str, Any]:
    """内容优化节点"""
    llm_service = LLMService()
    
    draft = state.get('draft', '')
    review_results = state.get('review_results', {})
    
    if not draft:
        return {
            "errors": state.get("errors", []) + ["没有可优化的内容"],
            "current_step": "optimization_failed"
        }
    
    # 构建优化提示词
    optimization_prompt = f"""
    请根据以下审核反馈优化内容：
    
    原始内容：
    {draft}
    
    审核反馈：
    {review_results.get('issues', [])}
    改进建议：
    {review_results.get('suggestions', [])}
    
    请优化内容，解决所有问题并采纳建议。
    """
    
    # 调用优化模型
    result = await llm_service.chat(
        endpoint_id=state.get('optimization_model', ''),
        prompt=optimization_prompt,
        temperature=0.5
    )
    
    # 更新优化轮数
    optimization_rounds = state.get('optimization_rounds', 0) + 1
    
    return {
        "optimized_content": result.get("content", ""),
        "optimization_rounds": optimization_rounds,
        "current_step": "optimization_completed",
        "metadata": {
            **state.get("metadata", {}),
            "optimization_round": optimization_rounds
        }
    }

