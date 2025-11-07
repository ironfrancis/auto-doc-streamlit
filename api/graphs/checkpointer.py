"""
LangGraph PostgreSQL Checkpointer 实现
"""
from typing import Any, Dict, Optional
from langgraph.checkpoint.base import BaseCheckpointSaver
from sqlalchemy.orm import Session
from api.database.connection import SessionLocal
from api.database.models import WorkflowExecution
import json


class PostgreSQLCheckpointer(BaseCheckpointSaver):
    """PostgreSQL Checkpointer 实现"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def put(self, config: Dict[str, Any], checkpoint: Dict[str, Any], metadata: Dict[str, Any], new_versions: Dict[str, Any]) -> Dict[str, Any]:
        """保存检查点"""
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return {}
        
        # 查找或创建工作流执行记录
        workflow = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == thread_id
        ).first()
        
        if not workflow:
            workflow = WorkflowExecution(
                workflow_id=thread_id,
                workflow_type=metadata.get("workflow_type", "unknown"),
                state=checkpoint,
                current_step=metadata.get("current_step", ""),
                status="running"
            )
            self.db.add(workflow)
        else:
            workflow.state = checkpoint
            workflow.current_step = metadata.get("current_step", workflow.current_step)
            if metadata.get("status"):
                workflow.status = metadata.get("status")
        
        self.db.commit()
        self.db.refresh(workflow)
        
        return {
            "config": config,
            "checkpoint": checkpoint,
            "metadata": metadata
        }
    
    def get(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取检查点"""
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None
        
        workflow = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == thread_id
        ).first()
        
        if not workflow:
            return None
        
        return {
            "config": config,
            "checkpoint": workflow.state or {},
            "metadata": {
                "workflow_type": workflow.workflow_type,
                "current_step": workflow.current_step,
                "status": workflow.status.value if hasattr(workflow.status, 'value') else str(workflow.status)
            }
        }
    
    def list(self, filter: Optional[Dict[str, Any]] = None, before: Optional[str] = None, limit: Optional[int] = None) -> list:
        """列出检查点"""
        query = self.db.query(WorkflowExecution)
        
        if filter:
            if "workflow_type" in filter:
                query = query.filter(WorkflowExecution.workflow_type == filter["workflow_type"])
            if "status" in filter:
                query = query.filter(WorkflowExecution.status == filter["status"])
        
        if limit:
            query = query.limit(limit)
        
        workflows = query.all()
        return [
            {
                "thread_id": w.workflow_id,
                "metadata": {
                    "workflow_type": w.workflow_type,
                    "current_step": w.current_step,
                    "status": w.status.value if hasattr(w.status, 'value') else str(w.status)
                }
            }
            for w in workflows
        ]
    
    def close(self):
        """关闭连接"""
        self.db.close()

