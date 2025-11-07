"""
智能审核和优化流程
"""
from langgraph.graph import StateGraph, END
from api.graphs.state import OptimizationState
from api.graphs.nodes.generation_node import generation_node
from api.graphs.nodes.review_node import review_node
from api.graphs.nodes.optimization_node import optimization_node
from api.graphs.nodes.publish_node import publish_node
from typing import Dict, Any


def should_continue_optimization(state: OptimizationState) -> str:
    """判断是否需要继续优化"""
    optimization_rounds = state.get("optimization_rounds", 0)
    max_rounds = state.get("max_optimization_rounds", 3)
    quality_score = state.get("quality_score", 0)
    
    if optimization_rounds >= max_rounds:
        return "final_review"
    if quality_score < 70:
        return "optimize"
    return "final_review"


def should_publish(state: OptimizationState) -> str:
    """判断是否应该发布"""
    should_publish_flag = state.get("should_publish", False)
    if should_publish_flag:
        return "publish"
    return "end"


async def final_review_node(state: OptimizationState) -> Dict[str, Any]:
    """最终审核节点"""
    # 使用审核节点进行最终审核
    review_result = await review_node(state)
    
    quality_score = review_result.get("quality_score", 0)
    should_publish_flag = quality_score >= 70
    
    return {
        **review_result,
        "should_publish": should_publish_flag,
        "current_step": "final_review_completed"
    }


def create_optimization_workflow(checkpointer=None):
    """创建智能审核和优化工作流图"""
    from api.graphs.checkpointer import PostgreSQLCheckpointer
    
    workflow = StateGraph(OptimizationState)
    
    # 添加节点
    workflow.add_node("generate", generation_node)
    workflow.add_node("review", review_node)
    workflow.add_node("optimize", optimization_node)
    workflow.add_node("final_review", final_review_node)
    workflow.add_node("publish", publish_node)
    
    # 设置入口点
    workflow.set_entry_point("generate")
    
    # 添加边
    workflow.add_edge("generate", "review")
    workflow.add_conditional_edges(
        "review",
        should_continue_optimization,
        {
            "optimize": "optimize",
            "final_review": "final_review"
        }
    )
    workflow.add_edge("optimize", "review")  # 优化后重新审核
    workflow.add_conditional_edges(
        "final_review",
        should_publish,
        {
            "publish": "publish",
            "end": END
        }
    )
    workflow.add_edge("publish", END)
    
    # 如果有 checkpointer，则使用它
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()

