"""
配置管理API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from api.database.connection import get_db
from api.database.models import ImageBed, WechatToken, InfoSource, Template, Config
from api.schemas.config import (
    ImageBed as ImageBedSchema,
    ImageBedCreate, ImageBedUpdate,
    WechatToken as WechatTokenSchema,
    WechatTokenCreate, WechatTokenUpdate,
    InfoSource as InfoSourceSchema,
    InfoSourceCreate, InfoSourceUpdate,
    Template as TemplateSchema,
    TemplateCreate, TemplateUpdate,
    Config as ConfigSchema,
    ConfigCreate, ConfigUpdate,
    BatchResponse
)

router = APIRouter(prefix="/config", tags=["配置管理"])


# 图床配置管理
@router.get("/image-beds", response_model=List[ImageBedSchema])
async def get_image_beds(
    skip: int = 0,
    limit: int = 100,
    enabled_only: bool = Query(False, description="只获取启用的图床"),
    db: Session = Depends(get_db)
):
    """获取图床配置列表"""
    query = db.query(ImageBed)
    if enabled_only:
        query = query.filter(ImageBed.is_enabled == "true")
    return query.offset(skip).limit(limit).all()


@router.get("/image-beds/default", response_model=Optional[ImageBedSchema])
async def get_default_image_bed(db: Session = Depends(get_db)):
    """获取默认图床"""
    return db.query(ImageBed).filter(ImageBed.is_default == "true").first()


@router.post("/image-beds", response_model=ImageBedSchema)
async def create_image_bed(
    image_bed: ImageBedCreate,
    db: Session = Depends(get_db)
):
    """创建图床配置"""
    # 如果设置为默认，先取消其他默认图床
    if image_bed.is_default:
        db.query(ImageBed).filter(ImageBed.is_default == "true").update(
            {"is_default": "false"}
        )

    db_image_bed = ImageBed(**image_bed.dict())
    db.add(db_image_bed)
    db.commit()
    db.refresh(db_image_bed)
    return db_image_bed


@router.put("/image-beds/{image_bed_id}", response_model=ImageBedSchema)
async def update_image_bed(
    image_bed_id: str,
    image_bed_update: ImageBedUpdate,
    db: Session = Depends(get_db)
):
    """更新图床配置"""
    db_image_bed = db.query(ImageBed).filter(ImageBed.id == image_bed_id).first()
    if not db_image_bed:
        raise HTTPException(status_code=404, detail="图床配置不存在")

    # 如果设置为默认，先取消其他默认图床
    update_data = image_bed_update.dict(exclude_unset=True)
    if update_data.get("is_default"):
        db.query(ImageBed).filter(ImageBed.id != image_bed_id).filter(
            ImageBed.is_default == "true"
        ).update({"is_default": "false"})

    for field, value in update_data.items():
        setattr(db_image_bed, field, value)

    db.commit()
    db.refresh(db_image_bed)
    return db_image_bed


@router.delete("/image-beds/{image_bed_id}")
async def delete_image_bed(image_bed_id: str, db: Session = Depends(get_db)):
    """删除图床配置"""
    db_image_bed = db.query(ImageBed).filter(ImageBed.id == image_bed_id).first()
    if not db_image_bed:
        raise HTTPException(status_code=404, detail="图床配置不存在")

    db.delete(db_image_bed)
    db.commit()
    return {"message": "图床配置已删除"}


# 微信Token管理
@router.get("/wechat-tokens", response_model=List[WechatTokenSchema])
async def get_wechat_tokens(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = Query(False, description="只获取活跃的Token"),
    db: Session = Depends(get_db)
):
    """获取微信Token列表"""
    query = db.query(WechatToken)
    if active_only:
        query = query.filter(WechatToken.status == "active")
    return query.offset(skip).limit(limit).all()


@router.post("/wechat-tokens", response_model=WechatTokenSchema)
async def create_wechat_token(
    token: WechatTokenCreate,
    db: Session = Depends(get_db)
):
    """创建微信Token"""
    db_token = WechatToken(**token.dict())
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


@router.put("/wechat-tokens/{token_id}", response_model=WechatTokenSchema)
async def update_wechat_token(
    token_id: str,
    token_update: WechatTokenUpdate,
    db: Session = Depends(get_db)
):
    """更新微信Token"""
    db_token = db.query(WechatToken).filter(WechatToken.id == token_id).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token不存在")

    update_data = token_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_token, field, value)

    db.commit()
    db.refresh(db_token)
    return db_token


@router.delete("/wechat-tokens/{token_id}")
async def delete_wechat_token(token_id: str, db: Session = Depends(get_db)):
    """删除微信Token"""
    db_token = db.query(WechatToken).filter(WechatToken.id == token_id).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token不存在")

    db.delete(db_token)
    db.commit()
    return {"message": "Token已删除"}


# 信息源管理
@router.get("/info-sources", response_model=List[InfoSourceSchema])
async def get_info_sources(
    skip: int = 0,
    limit: int = 100,
    source_type: Optional[str] = Query(None, description="信息源类型"),
    enabled_only: bool = Query(False, description="只获取启用的信息源"),
    db: Session = Depends(get_db)
):
    """获取信息源列表"""
    query = db.query(InfoSource)

    if source_type:
        query = query.filter(InfoSource.type == source_type)
    if enabled_only:
        query = query.filter(InfoSource.is_enabled == "true")

    return query.offset(skip).limit(limit).all()


@router.post("/info-sources", response_model=InfoSourceSchema)
async def create_info_source(
    info_source: InfoSourceCreate,
    db: Session = Depends(get_db)
):
    """创建信息源"""
    db_info_source = InfoSource(**info_source.dict())
    db.add(db_info_source)
    db.commit()
    db.refresh(db_info_source)
    return db_info_source


@router.put("/info-sources/{source_id}", response_model=InfoSourceSchema)
async def update_info_source(
    source_id: str,
    source_update: InfoSourceUpdate,
    db: Session = Depends(get_db)
):
    """更新信息源"""
    db_source = db.query(InfoSource).filter(InfoSource.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="信息源不存在")

    update_data = source_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_source, field, value)

    db.commit()
    db.refresh(db_source)
    return db_source


@router.delete("/info-sources/{source_id}")
async def delete_info_source(source_id: str, db: Session = Depends(get_db)):
    """删除信息源"""
    db_source = db.query(InfoSource).filter(InfoSource.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="信息源不存在")

    db.delete(db_source)
    db.commit()
    return {"message": "信息源已删除"}


# 模板管理
@router.get("/templates", response_model=List[TemplateSchema])
async def get_templates(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = Query(None, description="模板分类"),
    db: Session = Depends(get_db)
):
    """获取模板列表"""
    query = db.query(Template)
    if category:
        query = query.filter(Template.category == category)
    return query.offset(skip).limit(limit).all()


@router.get("/templates/default", response_model=Optional[TemplateSchema])
async def get_default_template(db: Session = Depends(get_db)):
    """获取默认模板"""
    return db.query(Template).filter(Template.is_default == "true").first()


@router.post("/templates", response_model=TemplateSchema)
async def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db)
):
    """创建模板"""
    # 如果设置为默认，先取消其他默认模板
    if template.is_default:
        db.query(Template).filter(Template.is_default == "true").update(
            {"is_default": "false"}
        )

    db_template = Template(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.put("/templates/{template_id}", response_model=TemplateSchema)
async def update_template(
    template_id: str,
    template_update: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """更新模板"""
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="模板不存在")

    update_data = template_update.dict(exclude_unset=True)
    if update_data.get("is_default"):
        db.query(Template).filter(Template.id != template_id).filter(
            Template.is_default == "true"
        ).update({"is_default": "false"})

    for field, value in update_data.items():
        setattr(db_template, field, value)

    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str, db: Session = Depends(get_db)):
    """删除模板"""
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="模板不存在")

    db.delete(db_template)
    db.commit()
    return {"message": "模板已删除"}


# 通用配置管理
@router.get("/configs", response_model=List[ConfigSchema])
async def get_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取配置列表"""
    return db.query(Config).offset(skip).limit(limit).all()


@router.get("/configs/{config_key}", response_model=ConfigSchema)
async def get_config(config_key: str, db: Session = Depends(get_db)):
    """获取特定配置"""
    config = db.query(Config).filter(Config.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config


@router.post("/configs", response_model=ConfigSchema)
async def create_config(
    config: ConfigCreate,
    db: Session = Depends(get_db)
):
    """创建配置"""
    db_config = Config(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@router.put("/configs/{config_key}", response_model=ConfigSchema)
async def update_config(
    config_key: str,
    config_update: ConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新配置"""
    db_config = db.query(Config).filter(Config.key == config_key).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")

    update_data = config_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)

    db.commit()
    db.refresh(db_config)
    return db_config


@router.delete("/configs/{config_key}")
async def delete_config(config_key: str, db: Session = Depends(get_db)):
    """删除配置"""
    db_config = db.query(Config).filter(Config.key == config_key).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")

    db.delete(db_config)
    db.commit()
    return {"message": "配置已删除"}

