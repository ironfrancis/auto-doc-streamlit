"""
发布节点
"""
from typing import Dict, Any
from api.graphs.state import WorkflowState
from api.services.article_service import ArticleService
from sqlalchemy.orm import Session
from api.database.connection import SessionLocal


async def publish_node(state: WorkflowState) -> Dict[str, Any]:
    """发布节点"""
    db = SessionLocal()
    try:
        article_service = ArticleService(db)
        
        # 获取最终内容
        final_content = state.get('optimized_content') or state.get('draft', '')
        
        if not final_content:
            return {
                "errors": state.get("errors", []) + ["没有可发布的内容"],
                "current_step": "publish_failed"
            }
        
        # 创建文章记录
        article_data = {
            "title": state.get("metadata", {}).get("title", "未命名文章"),
            "content": final_content,
            "channel_id": state.get("channel_id", ""),
            "status": "published",
            "metadata": state.get("metadata", {})
        }
        
        article = article_service.create_article(article_data)
        
        return {
            "final_output": final_content,
            "current_step": "publish_completed",
            "metadata": {
                **state.get("metadata", {}),
                "article_id": article.get("id"),
                "published_at": article.get("created_at")
            }
        }
    finally:
        db.close()

