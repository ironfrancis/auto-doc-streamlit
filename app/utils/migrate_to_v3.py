#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
频道数据迁移工具 - 迁移到V3结构
将旧的频道数据迁移到角色、任务、要求结构
"""

import json
import os
from pathlib import Path
from datetime import datetime

def migrate_channel_to_v3(old_channel):
    """将单个频道迁移到V3结构"""
    
    # 提取基本信息
    basic_info = {
        "name": old_channel.get("name", ""),
        "description": old_channel.get("description", "")[:100] if old_channel.get("description") else "",
        "template": old_channel.get("template", ""),
        "llm_endpoint": old_channel.get("llm_endpoint", ""),
        "created": old_channel.get("created_time", datetime.now().isoformat() + "Z"),
        "updated": old_channel.get("last_modified", datetime.now().isoformat() + "Z")
    }
    
    # 从custom_blocks中提取角色信息
    custom_blocks = old_channel.get("custom_blocks", {})
    
    # 构建角色
    role = {
        "identity": "",
        "team": "",
        "audience": "",
        "stance": ""
    }
    
    # 尝试从channel_identity中提取角色信息
    if "channel_identity" in custom_blocks:
        identity_content = custom_blocks["channel_identity"].get("content", "")
        # 简单的文本解析
        if "频道" in identity_content:
            role["identity"] = f"你是{old_channel['name']}的专业内容编辑"
        if "团队" in identity_content:
            role["team"] = "创新、前卫、极客的年轻技术团队"
        if "受众" in identity_content:
            if "高管" in identity_content or "投资人" in identity_content:
                role["audience"] = "互联网、AI行业前沿高管、投资人等"
            else:
                role["audience"] = "AI和技术圈子的专业人士"
        if "中立" in identity_content:
            role["stance"] = "保持客观中立的立场"
    
    # 构建任务
    task = {
        "main_goal": "根据原文进行深度观察和分析，产出高质量的内容",
        "output_format": "符合公众号爆款风格的文章",
        "word_count": "3000字左右",
        "special_notes": []
    }
    
    # 从writing_style中提取任务信息
    if "writing_style" in custom_blocks:
        style_content = custom_blocks["writing_style"].get("content", "")
        if "3000字" in style_content:
            task["word_count"] = "3000字左右"
        if "公众号" in style_content:
            task["output_format"] = "符合公众号爆款风格的文章"
        if "图片链接" in style_content:
            task["special_notes"].append("保留原文的图片链接")
    
    # 构建要求
    requirements = {
        "public_blocks": old_channel.get("selected_blocks", []),
        "custom_requirements": {}
    }
    
    # 从其他custom_blocks中提取自定义要求
    if "title_examples" in custom_blocks:
        requirements["custom_requirements"]["title_style"] = custom_blocks["title_examples"].get("content", "")[:200]
    
    if "avoid_requirements" in custom_blocks:
        requirements["custom_requirements"]["avoid"] = custom_blocks["avoid_requirements"].get("content", "")[:200]
    
    if "should_requirements" in custom_blocks:
        requirements["custom_requirements"]["should"] = custom_blocks["should_requirements"].get("content", "")[:200]
    
    # 生成ID
    channel_id = old_channel["name"].lower().replace(" ", "_").replace("（", "_").replace("）", "")
    channel_id = ''.join(c for c in channel_id if c.isalnum() or c == '_')
    
    return {
        "id": channel_id,
        "basic_info": basic_info,
        "role": role,
        "task": task,
        "requirements": requirements
    }

def migrate_all_channels():
    """迁移所有频道数据"""
    
    # 读取旧数据
    old_file = Path("app/channels_new.json")
    if not old_file.exists():
        print("❌ 找不到旧的频道文件")
        return False
    
    with open(old_file, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    # 迁移数据
    new_channels = []
    for old_channel in old_data.get("channels", []):
        try:
            new_channel = migrate_channel_to_v3(old_channel)
            new_channels.append(new_channel)
            print(f"✅ 迁移频道: {old_channel['name']}")
        except Exception as e:
            print(f"❌ 迁移失败 {old_channel.get('name', 'unknown')}: {e}")
    
    # 创建新的数据结构
    new_data = {
        "version": "3.0",
        "metadata": {
            "created_at": datetime.now().isoformat() + "Z",
            "description": "频道配置文件 - 角色任务要求结构版",
            "migrated_from": "channels_new.json",
            "migrated_at": datetime.now().isoformat() + "Z"
        },
        "channels": new_channels
    }
    
    # 保存新数据
    new_file = Path("app/channels_v3.json")
    with open(new_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 迁移完成！")
    print(f"  - 迁移频道数: {len(new_channels)}")
    print(f"  - 新文件: {new_file}")
    
    return True

if __name__ == "__main__":
    migrate_all_channels()
