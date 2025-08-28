#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
频道管理器 - 极简单页版本
只保留最核心的功能，确保稳定可用
"""

import streamlit as st
import json
import os
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="频道管理",
    layout="wide",
    page_icon="📺"
)

# 获取数据目录
def get_channels_file():
    """获取频道配置文件路径"""
    # 使用相对路径，避免复杂的导入
    base_dir = Path(__file__).parent.parent
    channels_file = base_dir / "channels_v3.json"
    return channels_file

def load_channels():
    """加载频道列表"""
    channels_file = get_channels_file()
    if channels_file.exists():
        try:
            with open(channels_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_channels(channels):
    """保存频道列表"""
    channels_file = get_channels_file()
    try:
        with open(channels_file, 'w', encoding='utf-8') as f:
            json.dump(channels, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def main():
    st.title("📺 频道管理")
    st.markdown("---")
    
    # 选择操作模式
    tab1, tab2, tab3 = st.tabs(["📋 频道列表", "➕ 新建频道", "🔧 快速编辑"])
    
    # 加载频道数据
    channels = load_channels()
    
    with tab1:
        # 频道列表
        if not channels:
            st.info("还没有频道，请在 新建频道 标签页创建")
        else:
            for idx, channel in enumerate(channels):
                with st.expander(f"**{channel.get('name', '未命名')}**", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**描述:** {channel.get('description', '无')}")
                        st.write(f"**模板:** {channel.get('template', '默认')}")
                        st.write(f"**LLM:** {channel.get('llm_endpoint', '默认')}")
                        
                        # 显示自定义块（如果有）
                        custom_blocks = channel.get('custom_blocks', {})
                        if custom_blocks:
                            st.write(f"**自定义块:** {len(custom_blocks)}个")
                    
                    with col2:
                        if st.button("🗑️ 删除", key=f"del_{idx}"):
                            channels.pop(idx)
                            if save_channels(channels):
                                st.success("删除成功")
                                st.rerun()
                            else:
                                st.error("删除失败")
    
    with tab2:
        # 新建频道
        st.markdown("### 创建新频道")
        
        with st.form("new_channel_form"):
            name = st.text_input("频道名称*", placeholder="输入唯一的频道名称")
            description = st.text_area("频道描述", placeholder="简单描述频道用途", height=100)
            template = st.text_input("HTML模板", value="默认模板")
            llm_endpoint = st.text_input("LLM端点", value="默认端点")
            
            # 简单的自定义提示词
            st.markdown("#### 自定义提示词（可选）")
            custom_prompt = st.text_area(
                "写作要求",
                placeholder="例如：保持专业的写作风格，使用简洁的语言...",
                height=150
            )
            
            submitted = st.form_submit_button("创建频道", type="primary")
            
            if submitted:
                if not name:
                    st.error("请输入频道名称")
                elif any(ch.get('name') == name for ch in channels):
                    st.error("频道名称已存在")
                else:
                    new_channel = {
                        'name': name,
                        'description': description,
                        'template': template,
                        'llm_endpoint': llm_endpoint,
                        'selected_blocks': [],
                        'custom_blocks': {}
                    }
                    
                    # 如果有自定义提示词，添加为自定义块
                    if custom_prompt.strip():
                        new_channel['custom_blocks']['custom_1'] = {
                            'name': '写作要求',
                            'content': custom_prompt.strip(),
                            'description': '用户自定义'
                        }
                    
                    channels.append(new_channel)
                    if save_channels(channels):
                        st.success(f"频道 '{name}' 创建成功！")
                        st.balloons()
                    else:
                        st.error("保存失败")
    
    with tab3:
        # 快速编辑
        st.markdown("### 快速编辑频道")
        
        if not channels:
            st.info("还没有频道可以编辑")
        else:
            # 选择要编辑的频道
            channel_names = [ch.get('name', '未命名') for ch in channels]
            selected_idx = st.selectbox(
                "选择频道",
                range(len(channel_names)),
                format_func=lambda x: channel_names[x]
            )
            
            if selected_idx is not None:
                channel = channels[selected_idx]
                
                st.markdown("---")
                
                # 编辑表单
                with st.form("edit_channel_form"):
                    # 基本信息（名称不可改）
                    st.text_input("频道名称", value=channel.get('name', ''), disabled=True)
                    new_desc = st.text_area("频道描述", value=channel.get('description', ''), height=100)
                    new_template = st.text_input("HTML模板", value=channel.get('template', ''))
                    new_llm = st.text_input("LLM端点", value=channel.get('llm_endpoint', ''))
                    
                    # 编辑自定义提示词
                    st.markdown("#### 自定义提示词")
                    custom_blocks = channel.get('custom_blocks', {})
                    custom_content = ""
                    if custom_blocks:
                        for block in custom_blocks.values():
                            custom_content = block.get('content', '')
                            break  # 只取第一个
                    
                    new_custom = st.text_area(
                        "写作要求",
                        value=custom_content,
                        height=150
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        save_btn = st.form_submit_button("💾 保存修改", type="primary", use_container_width=True)
                    with col2:
                        cancel_btn = st.form_submit_button("取消", use_container_width=True)
                    
                    if save_btn:
                        # 更新频道信息
                        channel['description'] = new_desc
                        channel['template'] = new_template
                        channel['llm_endpoint'] = new_llm
                        
                        # 更新自定义提示词
                        if new_custom.strip():
                            channel['custom_blocks'] = {
                                'custom_1': {
                                    'name': '写作要求',
                                    'content': new_custom.strip(),
                                    'description': '用户自定义'
                                }
                            }
                        else:
                            channel['custom_blocks'] = {}
                        
                        if save_channels(channels):
                            st.success("保存成功！")
                            st.rerun()
                        else:
                            st.error("保存失败")
    
    # 底部信息
    st.markdown("---")
    st.caption(f"共 {len(channels)} 个频道")

if __name__ == "__main__":
    main()
