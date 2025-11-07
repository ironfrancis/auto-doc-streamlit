"""
LangGraph 工作流 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from api.database.connection import get_db
from api.services.workflow_service import WorkflowService

router = APIRouter()


@router.post("/workflows/content-creation")
async def start_content_creation_workflow(
    workflow_data: dict, db: Session = Depends(get_db)
):
    """启动内容创作工作流"""
    service = WorkflowService(db)
    return service.start_workflow("content_creation", workflow_data)


@router.post("/workflows/multi-model")
async def start_multi_model_workflow(
    workflow_data: dict, db: Session = Depends(get_db)
):
    """启动多模型协作工作流"""
    service = WorkflowService(db)
    return service.start_workflow("multi_model", workflow_data)


@router.post("/workflows/optimization")
async def start_optimization_workflow(
    workflow_data: dict, db: Session = Depends(get_db)
):
    """启动智能审核优化工作流"""
    service = WorkflowService(db)
    return service.start_workflow("optimization", workflow_data)


@router.get("/workflows/{workflow_id}")
async def get_workflow_status(
    workflow_id: str, db: Session = Depends(get_db)
):
    """获取工作流执行状态"""
    service = WorkflowService(db)
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return workflow


@router.post("/workflows/{workflow_id}/continue")
async def continue_workflow(
    workflow_id: str, db: Session = Depends(get_db)
):
    """继续执行工作流"""
    service = WorkflowService(db)
    result = service.continue_workflow(workflow_id)
    if not result:
        raise HTTPException(status_code=404, detail="工作流不存在或无法继续")
    return result


@router.post("/workflows/{workflow_id}/pause")
async def pause_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """暂停工作流"""
    service = WorkflowService(db)
    success = service.pause_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return {"message": "工作流已暂停"}


@router.post("/workflows/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """取消工作流"""
    service = WorkflowService(db)
    success = service.cancel_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return {"message": "工作流已取消"}


@router.get("/workflows/{workflow_id}/history")
async def get_workflow_history(
    workflow_id: str, db: Session = Depends(get_db)
):
    """获取工作流执行历史"""
    service = WorkflowService(db)
    history = service.get_workflow_history(workflow_id)
    if not history:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return history

