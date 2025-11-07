"""
SQLAlchemy 数据库模型定义
"""
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid
from api.database.connection import Base


class WorkflowStatus(str, enum.Enum):
    """工作流状态枚举"""
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ArticleStatus(str, enum.Enum):
    """文章状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Channel(Base):
    """频道模型"""
    __tablename__ = "channels"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    template = Column(String)
    llm_endpoint = Column(String)
    # 使用 JSONB 存储灵活的配置数据
    content_rules = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    articles = relationship("Article", back_populates="channel")


class LLMEndpoint(Base):
    """LLM 端点配置模型"""
    __tablename__ = "llm_endpoints"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    api_type = Column(String, nullable=False)
    is_openai_compatible = Column(String, default="false")
    api_url = Column(String, nullable=False)
    api_key = Column(String)
    model = Column(String)
    temperature = Column(String, default="0.7")
    remark = Column(Text)
    is_default = Column(String, default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Article(Base):
    """文章模型"""
    __tablename__ = "articles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    content = Column(Text)
    channel_id = Column(String, ForeignKey("channels.id"))
    status = Column(SQLEnum(ArticleStatus), default=ArticleStatus.DRAFT)
    # 使用 JSONB 存储额外的元数据
    extra_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    channel = relationship("Channel", back_populates="articles")
    publish_history = relationship("PublishHistory", back_populates="article")


class PublishHistory(Base):
    """发布历史模型"""
    __tablename__ = "publish_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, ForeignKey("articles.id"))
    channel_id = Column(String, ForeignKey("channels.id"))
    publish_date = Column(DateTime(timezone=True))
    # 使用 JSONB 存储发布数据（阅读量、分享数等）
    publish_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    article = relationship("Article", back_populates="publish_history")


class WorkflowExecution(Base):
    """工作流执行记录模型"""
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    workflow_type = Column(String, nullable=False)  # content_creation/multi_model/optimization
    # 使用 JSONB 存储 LangGraph 状态
    state = Column(JSONB)
    current_step = Column(String)
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.RUNNING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ImageBed(Base):
    """图床配置模型"""
    __tablename__ = "image_beds"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # lsky, scdn等
    api_url = Column(String)
    token = Column(String)
    is_default = Column(String, default="false")
    is_enabled = Column(String, default="true")
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WechatToken(Base):
    """微信公众号Token配置"""
    __tablename__ = "wechat_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_name = Column(String, nullable=False)
    token = Column(String, nullable=False)
    status = Column(String, default="active")
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InfoSource(Base):
    """信息源配置模型"""
    __tablename__ = "info_sources"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    type = Column(String, nullable=False)  # rss, website, api等
    config = Column(JSONB)  # 存储额外的配置信息
    is_enabled = Column(String, default="true")
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Template(Base):
    """HTML模板配置模型"""
    __tablename__ = "templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    file_path = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # news, article, observation等
    is_default = Column(String, default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Config(Base):
    """系统配置模型"""
    __tablename__ = "configs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, nullable=False)
    value = Column(JSONB)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

