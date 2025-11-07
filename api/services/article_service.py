"""
文章业务逻辑服务
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from api.database.models import Article


class ArticleService:
    """文章服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_articles(
        self, skip: int = 0, limit: int = 100, channel_id: Optional[str] = None
    ) -> List[Dict]:
        """获取文章列表"""
        query = self.db.query(Article)
        if channel_id:
            query = query.filter(Article.channel_id == channel_id)
        articles = query.offset(skip).limit(limit).all()
        return [self._article_to_dict(art) for art in articles]
    
    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """根据ID获取文章"""
        article = self.db.query(Article).filter(Article.id == article_id).first()
        return self._article_to_dict(article) if article else None
    
    def create_article(self, article_data: Dict) -> Dict:
        """创建文章"""
        article = Article(**article_data)
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return self._article_to_dict(article)
    
    def update_article(self, article_id: str, article_data: Dict) -> Optional[Dict]:
        """更新文章"""
        article = self.db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return None
        
        for key, value in article_data.items():
            setattr(article, key, value)
        
        self.db.commit()
        self.db.refresh(article)
        return self._article_to_dict(article)
    
    def delete_article(self, article_id: str) -> bool:
        """删除文章"""
        article = self.db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return False
        
        self.db.delete(article)
        self.db.commit()
        return True
    
    def _article_to_dict(self, article: Article) -> Dict:
        """将文章模型转换为字典"""
        if not article:
            return None
        return {
            "id": article.id,
            "title": article.title,
            "content": article.content,
            "channel_id": article.channel_id,
            "status": article.status.value if hasattr(article.status, 'value') else str(article.status),
            "extra_metadata": article.extra_metadata if article.extra_metadata else {},
            "created_at": article.created_at.isoformat() if article.created_at else None,
            "updated_at": article.updated_at.isoformat() if article.updated_at else None,
        }

