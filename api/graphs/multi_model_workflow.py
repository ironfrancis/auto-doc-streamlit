"""
多模型协作工作流
"""
from langgraph.graph import StateGraph, END
from api.graphs.state import MultiModelState
from api.graphs.nodes.generation_node import generation_node
from api.graphs.nodes.review_node import review_node
from api.graphs.nodes.optimization_node import optimization_node
from typing import Dict, Any


async def task_decomposition_node(state: MultiModelState) -> Dict[str, Any]:
    """任务分解节点"""
    input_content = state.get("input_content", "")
    
    # 将任务分解为子任务
    tasks = [
        {"id": "task1", "type": "generation", "content": input_content},
        {"id": "task2", "type": "review", "content": ""},
        {"id": "task3", "type": "optimization", "content": ""}
    ]
    
    return {
        "tasks": tasks,
        "current_step": "task_decomposition_completed"
    }


async def model_assignment_node(state: MultiModelState) -> Dict[str, Any]:
    """模型分配节点"""
    tasks = state.get("tasks", [])
    
    # 为每个任务分配模型
    model_assignments = {}
    for task in tasks:
        task_type = task.get("type", "")
        if task_type == "generation":
            model_assignments[task["id"]] = state.get("llm_endpoint", "")
        elif task_type == "review":
            model_assignments[task["id"]] = state.get("review_model", "")
        elif task_type == "optimization":
            model_assignments[task["id"]] = state.get("optimization_model", "")
    
    return {
        "model_assignments": model_assignments,
        "current_step": "model_assignment_completed"
    }


async def parallel_execution_node(state: MultiModelState) -> Dict[str, Any]:
    """并行执行节点"""
    import asyncio
    
    tasks = state.get("tasks", [])
    model_assignments = state.get("model_assignments", {})
    parallel_results = {}
    
    # 并行执行所有任务
    async def execute_task(task):
        task_id = task["id"]
        task_type = task.get("type", "")
        model_id = model_assignments.get(task_id, "")
        
        if task_type == "generation":
            result = await generation_node(state)
            return task_id, result.get("draft", "")
        elif task_type == "review":
            result = await review_node(state)
            return task_id, result.get("review_results", {})
        elif task_type == "optimization":
            result = await optimization_node(state)
            return task_id, result.get("optimized_content", "")
        return task_id, None
    
    # 并行执行
    results = await asyncio.gather(*[execute_task(task) for task in tasks])
    
    for task_id, result in results:
        parallel_results[task_id] = result
    
    return {
        "parallel_results": parallel_results,
        "current_step": "parallel_execution_completed"
    }


async def merge_results_node(state: MultiModelState) -> Dict[str, Any]:
    """结果整合节点"""
    parallel_results = state.get("parallel_results", {})
    
    # 整合所有结果
    merged_result = ""
    for task_id, result in parallel_results.items():
        if isinstance(result, str):
            merged_result += result + "\n\n"
        elif isinstance(result, dict):
            merged_result += str(result) + "\n\n"
    
    return {
        "merged_result": merged_result.strip(),
        "current_step": "merge_completed"
    }


async def consistency_check_node(state: MultiModelState) -> Dict[str, Any]:
    """一致性检查节点"""
    merged_result = state.get("merged_result", "")
    
    # 简单的一致性检查
    consistency_check = len(merged_result) > 0
    
    return {
        "consistency_check": consistency_check,
        "final_output": merged_result if consistency_check else None,
        "current_step": "consistency_check_completed"
    }


def create_multi_model_workflow(checkpointer=None):
    """创建多模型协作工作流图"""
    from api.graphs.checkpointer import PostgreSQLCheckpointer
    
    workflow = StateGraph(MultiModelState)
    
    # 添加节点
    workflow.add_node("decompose", task_decomposition_node)
    workflow.add_node("assign", model_assignment_node)
    workflow.add_node("execute", parallel_execution_node)
    workflow.add_node("merge", merge_results_node)
    workflow.add_node("check", consistency_check_node)
    
    # 设置入口点和边
    workflow.set_entry_point("decompose")
    workflow.add_edge("decompose", "assign")
    workflow.add_edge("assign", "execute")
    workflow.add_edge("execute", "merge")
    workflow.add_edge("merge", "check")
    workflow.add_edge("check", END)
    
    # 如果有 checkpointer，则使用它
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()

