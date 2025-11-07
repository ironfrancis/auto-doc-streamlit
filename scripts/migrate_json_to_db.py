"""
JSON 数据到 PostgreSQL 的迁移脚本
"""
import json
import os
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from api.database.connection import SessionLocal, engine, Base
from api.database.models import Channel, LLMEndpoint, Article, PublishHistory, Config

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_json_file(file_path: Path) -> dict:
    """加载 JSON 文件"""
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def migrate_channels(db: Session, config_dir: Path):
    """迁移频道数据"""
    channels_file = config_dir / "channels_v3.json"
    if not channels_file.exists():
        print("频道配置文件不存在，跳过迁移")
        return
    
    data = load_json_file(channels_file)
    channels = data.get("channels", [])
    
    for channel_data in channels:
        # 检查是否已存在
        existing = db.query(Channel).filter(Channel.id == channel_data.get("id")).first()
        if existing:
            print(f"频道 {channel_data.get('name')} 已存在，跳过")
            continue
        
        channel = Channel(
            id=channel_data.get("id"),
            name=channel_data.get("name"),
            description=channel_data.get("description"),
            template=channel_data.get("template"),
            llm_endpoint=channel_data.get("llm_endpoint"),
            content_rules=channel_data.get("content_rules", {})
        )
        db.add(channel)
    
    db.commit()
    print(f"成功迁移 {len(channels)} 个频道")


def migrate_llm_endpoints(db: Session, config_dir: Path):
    """迁移 LLM 端点数据"""
    endpoints_file = config_dir / "llm_endpoints.json"
    if not endpoints_file.exists():
        print("LLM 端点配置文件不存在，跳过迁移")
        return
    
    endpoints = load_json_file(endpoints_file)
    if not isinstance(endpoints, list):
        endpoints = []
    
    for endpoint_data in endpoints:
        # 检查是否已存在
        existing = db.query(LLMEndpoint).filter(
            LLMEndpoint.name == endpoint_data.get("name")
        ).first()
        if existing:
            print(f"LLM 端点 {endpoint_data.get('name')} 已存在，跳过")
            continue
        
        endpoint = LLMEndpoint(
            name=endpoint_data.get("name"),
            api_type=endpoint_data.get("api_type", "OpenAI"),
            is_openai_compatible=str(endpoint_data.get("is_openai_compatible", False)),
            api_url=endpoint_data.get("api_url"),
            api_key=endpoint_data.get("api_key", ""),
            model=endpoint_data.get("model"),
            temperature=str(endpoint_data.get("temperature", 0.7)),
            remark=endpoint_data.get("remark"),
            is_default=str(endpoint_data.get("default", False))
        )
        db.add(endpoint)
    
    db.commit()
    print(f"成功迁移 {len(endpoints)} 个 LLM 端点")


def migrate_articles(db: Session, workspace_dir: Path):
    """迁移文章数据"""
    # 从 md_transcribe_history.json 迁移
    history_file = workspace_dir / "data" / "json" / "md_transcribe_history.json"
    if not history_file.exists():
        print("文章历史文件不存在，跳过迁移")
        return
    
    articles_data = load_json_file(history_file)
    if not isinstance(articles_data, list):
        articles_data = []
    
    for article_data in articles_data:
        # 检查是否已存在
        existing = db.query(Article).filter(Article.id == article_data.get("id")).first()
        if existing:
            continue
        
        # 查找对应的频道
        channel_name = article_data.get("channel", "")
        channel = db.query(Channel).filter(Channel.name == channel_name).first()
        channel_id = channel.id if channel else None
        
        article = Article(
            id=article_data.get("id"),
            title=article_data.get("title", "未命名文章"),
            content=article_data.get("md_result", ""),
            channel_id=channel_id,
            status="published",
            metadata={
                "input_type": article_data.get("input_type"),
                "input_content": article_data.get("input_content", ""),
                "created_at": article_data.get("created_at")
            }
        )
        db.add(article)
    
    db.commit()
    print(f"成功迁移 {len(articles_data)} 篇文章")


def main():
    """主函数"""
    print("开始迁移 JSON 数据到 PostgreSQL...")
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")
    
    # 获取配置目录
    project_root = Path(__file__).parent.parent
    config_dir = project_root / "config"
    workspace_dir = project_root / "workspace"
    
    db = SessionLocal()
    try:
        # 迁移数据
        migrate_channels(db, config_dir)
        migrate_llm_endpoints(db, config_dir)
        migrate_articles(db, workspace_dir)
        
        print("数据迁移完成！")
    except Exception as e:
        print(f"迁移过程中出现错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

