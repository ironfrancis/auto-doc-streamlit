#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置迁移脚本
将config目录下的JSON配置文件迁移到数据库中
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 直接使用本地数据库连接字符串
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/autodoc"
)

# 创建数据库引擎
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)

# 导入模型（这里会导入Base）
from api.database.models import (
    ImageBed, WechatToken, InfoSource, Template, Config,
    LLMEndpoint, Channel, Base
)
from api.schemas.config import (
    ImageBedCreate, WechatTokenCreate, InfoSourceCreate,
    TemplateCreate, ConfigCreate
)
from sqlalchemy.orm import Session, sessionmaker

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")


def migrate_llm_endpoints(db: Session, config_file: Path):
    """迁移LLM端点配置"""
    if not config_file.exists():
        print(f"⚠️  LLM端点配置文件不存在: {config_file}")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        endpoints = json.load(f)

    migrated_count = 0
    for endpoint_data in endpoints:
        # 检查是否已存在
        existing = db.query(LLMEndpoint).filter(
            LLMEndpoint.name == endpoint_data.get('name')
        ).first()

        if existing:
            print(f"⏭️  LLM端点已存在，跳过: {endpoint_data.get('name')}")
            continue

        # 转换数据格式
        db_endpoint = LLMEndpoint(
            name=endpoint_data.get('name'),
            api_type=endpoint_data.get('api_type'),
            is_openai_compatible=str(endpoint_data.get('is_openai_compatible', False)).lower(),
            api_url=endpoint_data.get('api_url'),
            api_key=endpoint_data.get('api_key'),
            model=endpoint_data.get('model'),
            temperature=str(endpoint_data.get('temperature', 0.7)),
            remark=endpoint_data.get('remark'),
            is_default=str(endpoint_data.get('default', False)).lower()
        )

        db.add(db_endpoint)
        migrated_count += 1
        print(f"✅ 迁移LLM端点: {endpoint_data.get('name')}")

    db.commit()
    print(f"📊 LLM端点迁移完成，共迁移 {migrated_count} 个端点")


def migrate_channels(db: Session, config_file: Path):
    """迁移频道配置"""
    if not config_file.exists():
        print(f"⚠️  频道配置文件不存在: {config_file}")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        channels_data = json.load(f)

    migrated_count = 0
    for channel_data in channels_data.get('channels', []):
        # 检查是否已存在
        existing = db.query(Channel).filter(
            Channel.name == channel_data.get('name')
        ).first()

        if existing:
            print(f"⏭️  频道已存在，跳过: {channel_data.get('name')}")
            continue

        # 转换数据格式
        db_channel = Channel(
            name=channel_data.get('name'),
            description=channel_data.get('description'),
            template=channel_data.get('template'),
            llm_endpoint=channel_data.get('llm_endpoint'),
            content_rules=channel_data.get('content_rules')
        )

        db.add(db_channel)
        migrated_count += 1
        print(f"✅ 迁移频道: {channel_data.get('name')}")

    db.commit()
    print(f"📊 频道迁移完成，共迁移 {migrated_count} 个频道")


def migrate_image_beds(db: Session, config_file: Path):
    """迁移图床配置"""
    if not config_file.exists():
        print(f"⚠️  图床配置文件不存在: {config_file}")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        beds_data = json.load(f)

    migrated_count = 0
    for bed_data in beds_data.get('image_beds', []):
        # 检查是否已存在
        existing = db.query(ImageBed).filter(
            ImageBed.name == bed_data.get('name')
        ).first()

        if existing:
            print(f"⏭️  图床已存在，跳过: {bed_data.get('name')}")
            continue

        # 转换数据格式
        db_bed = ImageBed(
            name=bed_data.get('name'),
            type=bed_data.get('type'),
            api_url=bed_data.get('api_url'),
            token=bed_data.get('token'),
            is_default=str(bed_data.get('default', False)).lower(),
            is_enabled=str(bed_data.get('enabled', True)).lower(),
            description=bed_data.get('description')
        )

        db.add(db_bed)
        migrated_count += 1
        print(f"✅ 迁移图床: {bed_data.get('name')}")

    db.commit()
    print(f"📊 图床迁移完成，共迁移 {migrated_count} 个图床")


def migrate_wechat_tokens(db: Session, config_file: Path):
    """迁移微信Token配置"""
    if not config_file.exists():
        print(f"⚠️  微信Token配置文件不存在: {config_file}")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        tokens_data = json.load(f)

    migrated_count = 0
    tokens = tokens_data.get('tokens', {})
    for account_name, token_data in tokens.items():
        # 检查是否已存在
        existing = db.query(WechatToken).filter(
            WechatToken.account_name == account_name
        ).first()

        if existing:
            print(f"⏭️  微信Token已存在，跳过: {account_name}")
            continue

        # 转换数据格式
        db_token = WechatToken(
            account_name=account_name,
            token=token_data.get('token'),
            status=token_data.get('status', 'active'),
            description=token_data.get('description')
        )

        db.add(db_token)
        migrated_count += 1
        print(f"✅ 迁移微信Token: {account_name}")

    db.commit()
    print(f"📊 微信Token迁移完成，共迁移 {migrated_count} 个Token")


def migrate_info_sources(db: Session, config_file: Path):
    """迁移信息源配置"""
    if not config_file.exists():
        print(f"⚠️  信息源配置文件不存在: {config_file}")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        sources_data = json.load(f)

    migrated_count = 0
    # info_sources.json 是一个直接的数组
    sources = sources_data if isinstance(sources_data, list) else sources_data.get('sources', [])
    for source_data in sources:
        # 使用title作为name，如果没有则使用url
        name = source_data.get('title') or source_data.get('url', 'Unknown')

        # 检查是否已存在
        existing = db.query(InfoSource).filter(
            InfoSource.name == name
        ).first()

        if existing:
            print(f"⏭️  信息源已存在，跳过: {name}")
            continue

        # 转换数据格式，默认类型为website
        db_source = InfoSource(
            name=name,
            url=source_data.get('url'),
            type=source_data.get('type', 'website'),
            config=source_data.get('config'),
            is_enabled=str(source_data.get('enabled', True)).lower(),
            description=source_data.get('description', source_data.get('title'))
        )

        db.add(db_source)
        migrated_count += 1
        print(f"✅ 迁移信息源: {name}")

    db.commit()
    print(f"📊 信息源迁移完成，共迁移 {migrated_count} 个信息源")


def migrate_templates(db: Session, config_file: Path):
    """迁移模板配置"""
    if not config_file.exists():
        print(f"⚠️  模板配置文件不存在: {config_file}")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        templates_data = json.load(f)

    migrated_count = 0
    # template_info.json 的键就是文件名，值包含模板信息
    for file_name, template_data in templates_data.items():
        # 使用文件名作为name，如果没有则使用template_data中的name
        name = template_data.get('name', file_name)

        # 检查是否已存在
        existing = db.query(Template).filter(
            Template.name == name
        ).first()

        if existing:
            print(f"⏭️  模板已存在，跳过: {name}")
            continue

        # 转换数据格式
        db_template = Template(
            name=name,
            file_path=file_name,  # 使用键作为文件路径
            description=template_data.get('description'),
            category=template_data.get('category'),
            is_default=str(template_data.get('default', False)).lower()
        )

        db.add(db_template)
        migrated_count += 1
        print(f"✅ 迁移模板: {name}")

    db.commit()
    print(f"📊 模板迁移完成，共迁移 {migrated_count} 个模板")


def main():
    """主函数"""
    config_dir = project_root / "config"

    print("🚀 开始配置迁移...")
    print(f"📁 配置目录: {config_dir}")

    # 创建数据库表
    create_tables()

    # 创建数据库会话
    db = SessionLocal()

    try:
        # 迁移各种配置
        migrate_llm_endpoints(db, config_dir / "llm_endpoints.json")
        migrate_channels(db, config_dir / "channels_v3.json")
        migrate_image_beds(db, config_dir / "image_beds.json")
        migrate_wechat_tokens(db, config_dir / "tokens_config.json")
        migrate_info_sources(db, config_dir / "info_sources.json")
        migrate_templates(db, config_dir / "template_info.json")

        print("\n🎉 配置迁移完成！")

    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()