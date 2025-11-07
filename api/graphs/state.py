"""
LangGraph 工作流状态定义
"""
from typing import TypedDict, List, Dict, Optional, Any
from typing_extensions import Annotated
from langgraph.graph.message import add_messages


class WorkflowState(TypedDict):
    """工作流状态基类"""
    # 输入数据
    input_content: str
    channel_id: str
    channel_config: Dict[str, Any]
    
    # 中间结果
    draft: Optional[str]
    optimized_content: Optional[str]
    review_results: Optional[Dict[str, Any]]
    
    # 最终输出
    final_output: Optional[str]
    
    # 元数据
    metadata: Dict[str, Any]
    current_step: str
    errors: List[str]
    warnings: List[str]


class ContentCreationState(WorkflowState):
    """内容创作工作流状态"""
    prompt_blocks: List[str]
    llm_endpoint: str
    quality_score: Optional[float]
    needs_optimization: bool


class MultiModelState(WorkflowState):
    """多模型协作工作流状态"""
    tasks: List[Dict[str, Any]]
    model_assignments: Dict[str, str]
    parallel_results: Dict[str, Any]
    merged_result: Optional[str]
    consistency_check: Optional[bool]


class OptimizationState(WorkflowState):
    """智能审核和优化工作流状态"""
    review_model: str
    optimization_model: str
    review_score: Optional[float]
    optimization_rounds: int
    max_optimization_rounds: int
    should_publish: Optional[bool]
    publish_channel: Optional[str]

