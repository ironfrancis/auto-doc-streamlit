"""
文章管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from api.database.connection import get_db
from api.services.article_service import ArticleService

router = APIRouter()


@router.get("/articles")
async def get_articles(
    skip: int = 0,
    limit: int = 100,
    channel_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取文章列表"""
    service = ArticleService(db)
    return service.get_articles(skip=skip, limit=limit, channel_id=channel_id)


@router.get("/articles/{article_id}")
async def get_article(article_id: str, db: Session = Depends(get_db)):
    """获取单个文章"""
    service = ArticleService(db)
    article = service.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article


@router.post("/articles")
async def create_article(article_data: dict, db: Session = Depends(get_db)):
    """创建文章"""
    service = ArticleService(db)
    return service.create_article(article_data)


@router.put("/articles/{article_id}")
async def update_article(
    article_id: str, article_data: dict, db: Session = Depends(get_db)
):
    """更新文章"""
    service = ArticleService(db)
    article = service.update_article(article_id, article_data)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article


@router.delete("/articles/{article_id}")
async def delete_article(article_id: str, db: Session = Depends(get_db)):
    """删除文章"""
    service = ArticleService(db)
    success = service.delete_article(article_id)
    if not success:
        raise HTTPException(status_code=404, detail="文章不存在")
    return {"message": "文章已删除"}

