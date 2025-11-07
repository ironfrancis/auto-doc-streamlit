"""
工作流管理服务
"""
from sqlalchemy.orm import Session
from typing import Dict, Optional
from api.database.models import WorkflowExecution
from api.graphs.checkpointer import PostgreSQLCheckpointer
from api.graphs.content_creation_graph import create_content_creation_graph
from api.graphs.multi_model_workflow import create_multi_model_workflow
from api.graphs.optimization_workflow import create_optimization_workflow
import uuid
import asyncio


class WorkflowService:
    """工作流服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.checkpointer = PostgreSQLCheckpointer()
    
    def _get_workflow_graph(self, workflow_type: str):
        """获取工作流图"""
        if workflow_type == "content_creation":
            return create_content_creation_graph(self.checkpointer)
        elif workflow_type == "multi_model":
            return create_multi_model_workflow(self.checkpointer)
        elif workflow_type == "optimization":
            return create_optimization_workflow(self.checkpointer)
        else:
            raise ValueError(f"未知的工作流类型: {workflow_type}")
    
    def start_workflow(self, workflow_type: str, workflow_data: Dict) -> Dict:
        """启动工作流"""
        workflow_id = str(uuid.uuid4())
        workflow = WorkflowExecution(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            state=workflow_data,
            status="running"
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        
        # 启动 LangGraph 工作流
        try:
            graph = self._get_workflow_graph(workflow_type)
            config = {"configurable": {"thread_id": workflow_id}}
            
            # 异步执行工作流
            asyncio.create_task(
                graph.ainvoke(workflow_data, config=config)
            )
        except Exception as e:
            workflow.status = "failed"
            self.db.commit()
            raise e
        
        return {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "status": "running"
        }
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """获取工作流状态"""
        workflow = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        ).first()
        if not workflow:
            return None
        return self._workflow_to_dict(workflow)
    
    def continue_workflow(self, workflow_id: str) -> Optional[Dict]:
        """继续执行工作流"""
        workflow = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        ).first()
        if not workflow or workflow.status != "paused":
            return None
        
        workflow.status = "running"
        self.db.commit()
        
        # 继续执行 LangGraph 工作流
        try:
            graph = self._get_workflow_graph(workflow.workflow_type)
            config = {"configurable": {"thread_id": workflow_id}}
            
            # 从检查点恢复状态
            state = workflow.state or {}
            
            # 异步继续执行
            asyncio.create_task(
                graph.ainvoke(state, config=config)
            )
        except Exception as e:
            workflow.status = "failed"
            self.db.commit()
            raise e
        
        return self._workflow_to_dict(workflow)
    
    def pause_workflow(self, workflow_id: str) -> bool:
        """暂停工作流"""
        workflow = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        ).first()
        if not workflow:
            return False
        
        workflow.status = "paused"
        self.db.commit()
        return True
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """取消工作流"""
        workflow = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        ).first()
        if not workflow:
            return False
        
        workflow.status = "cancelled"
        self.db.commit()
        return True
    
    def get_workflow_history(self, workflow_id: str) -> Optional[Dict]:
        """获取工作流执行历史"""
        workflow = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        ).first()
        if not workflow:
            return None
        
        return {
            "workflow_id": workflow.workflow_id,
            "workflow_type": workflow.workflow_type,
            "status": workflow.status,
            "current_step": workflow.current_step,
            "state": workflow.state,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
        }
    
    def _workflow_to_dict(self, workflow: WorkflowExecution) -> Dict:
        """将工作流模型转换为字典"""
        if not workflow:
            return None
        return {
            "workflow_id": workflow.workflow_id,
            "workflow_type": workflow.workflow_type,
            "status": workflow.status,
            "current_step": workflow.current_step,
            "state": workflow.state,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
        }

