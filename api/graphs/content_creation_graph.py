"""
内容创作工作流（多步骤、有状态）
"""
from langgraph.graph import StateGraph, END
from api.graphs.state import ContentCreationState
from api.graphs.nodes.generation_node import generation_node
from api.graphs.nodes.review_node import review_node
from api.graphs.nodes.optimization_node import optimization_node
from api.graphs.nodes.publish_node import publish_node
from api.graphs.checkpointer import PostgreSQLCheckpointer


def should_optimize(state: ContentCreationState) -> str:
    """判断是否需要优化"""
    if state.get("needs_optimization", False):
        return "optimize"
    return "publish"


def create_content_creation_graph(checkpointer: PostgreSQLCheckpointer = None):
    """创建内容创作工作流图"""
    workflow = StateGraph(ContentCreationState)
    
    # 添加节点
    workflow.add_node("generate", generation_node)
    workflow.add_node("review", review_node)
    workflow.add_node("optimize", optimization_node)
    workflow.add_node("publish", publish_node)
    
    # 设置入口点
    workflow.set_entry_point("generate")
    
    # 添加边
    workflow.add_edge("generate", "review")
    workflow.add_conditional_edges(
        "review",
        should_optimize,
        {
            "optimize": "optimize",
            "publish": "publish"
        }
    )
    workflow.add_edge("optimize", "review")  # 优化后重新审核
    workflow.add_edge("publish", END)
    
    # 如果有 checkpointer，则使用它
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()

