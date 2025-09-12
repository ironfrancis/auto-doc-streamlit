#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可复用的UI组件模块
提供频道表单、提示词块表单、确认对话框、数据预览等组件
"""

import streamlit as st
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

def render_channel_form(channel_data: Dict = None, mode: str = "create", 
                       template_files: List[str] = None, endpoint_names: List[str] = None,
                       on_save: Callable = None, on_cancel: Callable = None) -> Dict:
    """
    渲染频道表单
    
    Args:
        channel_data: 频道数据，编辑模式下使用
        mode: 模式，"create" 或 "edit"
        template_files: 可用的HTML模板文件列表
        endpoint_names: 可用的LLM端点名称列表
        on_save: 保存回调函数
        on_cancel: 取消回调函数
    
    Returns:
        表单数据字典
    """
    if channel_data is None:
        channel_data = {}
    
    if template_files is None:
        template_files = []
    
    if endpoint_names is None:
        endpoint_names = []
    
    # 基本信息表单
    st.markdown("### 📝 频道基本信息")
    
    # 频道名称
    name = st.text_input(
        "频道名称", 
        value=channel_data.get("name", ""),
        key=f"channel_name_{mode}_{id(channel_data)}", 
        placeholder="请输入频道名称..."
    )
    
    # 频道描述
    description = st.text_area(
        "频道描述", 
        value=channel_data.get("description", ""),
        height=80, 
        key=f"channel_desc_{mode}_{id(channel_data)}", 
        placeholder="请输入频道描述..."
    )
    
    # 模板和端点选择
    col_template, col_endpoint = st.columns(2)
    
    with col_template:
        current_template = channel_data.get("template", template_files[0] if template_files else "")
        template_index = template_files.index(current_template) if current_template in template_files else 0
        template = st.selectbox(
            "HTML模板", 
            template_files, 
            index=template_index,
            key=f"channel_template_{mode}_{id(channel_data)}",
            help="选择用于渲染文章的HTML模板"
        )
    
    with col_endpoint:
        current_endpoint = channel_data.get("llm_endpoint", endpoint_names[0] if endpoint_names else "")
        endpoint_index = endpoint_names.index(current_endpoint) if current_endpoint in endpoint_names else 0
        endpoint = st.selectbox(
            "LLM端点", 
            endpoint_names, 
            index=endpoint_index,
            key=f"channel_endpoint_{mode}_{id(channel_data)}",
            help="选择用于AI创作的LLM端点"
        )
    
    # 操作按钮
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        if st.button("💾 保存", key=f"save_{mode}_{id(channel_data)}", type="primary"):
            if not name.strip():
                st.error("请输入频道名称！")
                return None
            
            form_data = {
                "name": name.strip(),
                "description": description.strip(),
                "template": template,
                "llm_endpoint": endpoint
            }
            
            if on_save:
                on_save(form_data)
            return form_data
    
    with col_cancel:
        if st.button("❌ 取消", key=f"cancel_{mode}_{id(channel_data)}"):
            if on_cancel:
                on_cancel()
            return None
    
    return None

def render_prompt_block_form(block_data: Dict = None, mode: str = "create",
                           on_save: Callable = None, on_cancel: Callable = None) -> Dict:
    """
    渲染提示词块表单
    
    Args:
        block_data: 提示词块数据，编辑模式下使用
        mode: 模式，"create" 或 "edit"
        on_save: 保存回调函数
        on_cancel: 取消回调函数
    
    Returns:
        表单数据字典
    """
    if block_data is None:
        block_data = {}
    
    # 提示词块表单
    st.markdown("### 📝 提示词块信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input(
            "块名称", 
            value=block_data.get("name", ""),
            key=f"block_name_{mode}_{id(block_data)}", 
            placeholder="例如：基础语言风格要求"
        )
        
        description = st.text_area(
            "块描述", 
            value=block_data.get("description", ""),
            height=80, 
            key=f"block_desc_{mode}_{id(block_data)}", 
            placeholder="描述这个块的作用和特点"
        )
    
    with col2:
        category = st.selectbox(
            "块分类", 
            ["public", "industry"], 
            index=0 if block_data.get('category') == "public" else 1,
            key=f"block_category_{mode}_{id(block_data)}",
            help="public: 公共通用块, industry: 行业特定块"
        )
        
        content = st.text_area(
            "块内容", 
            value=block_data.get("content", ""),
            height=120, 
            key=f"block_content_{mode}_{id(block_data)}", 
            placeholder="输入提示词内容..."
        )
    
    # 操作按钮
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        if st.button("💾 保存", key=f"save_block_{mode}_{id(block_data)}", type="primary"):
            if not name or not description or not content:
                st.warning("请填写完整的块信息")
                return None
            
            form_data = {
                "name": name.strip(),
                "description": description.strip(),
                "content": content.strip(),
                "category": category
            }
            
            if on_save:
                on_save(form_data)
            return form_data
    
    with col_cancel:
        if st.button("❌ 取消", key=f"cancel_block_{mode}_{id(block_data)}"):
            if on_cancel:
                on_cancel()
            return None
    
    return None

def render_confirmation_dialog(message: str, on_confirm: Callable = None, 
                             on_cancel: Callable = None, confirm_text: str = "确认", 
                             cancel_text: str = "取消") -> bool:
    """
    渲染确认对话框
    
    Args:
        message: 确认消息
        on_confirm: 确认回调函数
        on_cancel: 取消回调函数
        confirm_text: 确认按钮文本
        cancel_text: 取消按钮文本
    
    Returns:
        是否确认
    """
    st.warning(message)
    
    col_confirm, col_cancel = st.columns(2)
    
    with col_confirm:
        if st.button(f"✅ {confirm_text}", key=f"confirm_{id(message)}"):
            if on_confirm:
                on_confirm()
            return True
    
    with col_cancel:
        if st.button(f"❌ {cancel_text}", key=f"cancel_{id(message)}"):
            if on_cancel:
                on_cancel()
            return False
    
    return False

def render_data_preview(data: Dict, title: str = "数据预览") -> None:
    """
    渲染数据预览
    
    Args:
        data: 要预览的数据
        title: 预览标题
    """
    st.markdown(f"### 👀 {title}")
    
    if not data:
        st.info("暂无数据")
        return
    
    # 基本信息
    if 'name' in data:
        st.info(f"**名称:** {data.get('name', '未设置')}")
    
    if 'description' in data:
        st.info(f"**描述:** {data.get('description', '未设置')}")
    
    if 'template' in data:
        st.info(f"**HTML模板:** {data.get('template', '未选择')}")
    
    if 'llm_endpoint' in data:
        st.info(f"**LLM端点:** {data.get('llm_endpoint', '未选择')}")
    
    # 时间信息
    if 'created_time' in data:
        st.write(f"**创建时间:** {data['created_time']}")
    
    if 'last_modified' in data:
        st.write(f"**最后修改:** {data['last_modified']}")

def render_endpoint_info(endpoint_name: str, endpoints: List[Dict]) -> None:
    """
    渲染端点详细信息
    
    Args:
        endpoint_name: 端点名称
        endpoints: 端点列表
    """
    if not endpoint_name or not endpoints:
        return
    
    selected_endpoint = next((ep for ep in endpoints if ep["name"] == endpoint_name), None)
    
    if selected_endpoint:
        st.markdown("#### 🤖 LLM端点信息")
        st.success(f"**端点名称:** {endpoint_name}")
        st.info(f"**API地址:** {selected_endpoint.get('api_url', '未配置')}")
        st.info(f"**模型名称:** {selected_endpoint.get('model', '未配置')}")
        st.info(f"**API类型:** {selected_endpoint.get('api_type', 'OpenAI兼容')}")
    else:
        st.warning(f"⚠️ 端点 '{endpoint_name}' 配置信息不完整")

def render_prompt_blocks_selection(public_blocks: Dict, industry_blocks: Dict, 
                                 selected_blocks: List[str] = None,
                                 blocks_per_row: int = 4,
                                 compact_mode: bool = False) -> List[str]:
    """
    渲染提示词块选择界面 - 优化版
    使用并排布局，减少页面高度占用
    
    Args:
        public_blocks: 公共提示词块
        industry_blocks: 行业提示词块
        selected_blocks: 已选择的块ID列表
        blocks_per_row: 每行显示的块数量
        compact_mode: 紧凑模式，减少间距和描述显示
    
    Returns:
        选中的块ID列表
    """
    if selected_blocks is None:
        selected_blocks = []
    
    selected_public = []
    selected_industry = []
    
    # 公共提示词块 - 使用并排布局
    if public_blocks:
        st.markdown("#### 🌍 公共提示词块")
        
        # 将公共块分组，确保每行都有固定数量的列
        public_block_items = list(public_blocks.items())
        for i in range(0, len(public_block_items), blocks_per_row):
            row_blocks = public_block_items[i:i + blocks_per_row]
            
            # 创建固定数量的列，确保对齐
            cols = st.columns(blocks_per_row)
            
            for j in range(blocks_per_row):
                with cols[j]:
                    if j < len(row_blocks):
                        # 有块的行
                        block_id, block = row_blocks[j]
                        is_selected = block_id in selected_blocks
                        if st.checkbox(
                            f"✅ {block['name']}", 
                            value=is_selected,
                            key=f"public_{block_id}",
                            help=block.get('description', ''),
                            label_visibility="collapsed"
                        ):
                            selected_public.append(block_id)
                        
                        # 显示描述提示
                        if block.get('description'):
                            desc = block['description']
                            if len(desc) > 25:
                                st.caption(desc[:25] + "...")
                            else:
                                st.caption(desc)
                    else:
                        # 空列，保持对齐
                        st.write("")
    
    # 行业提示词块 - 使用并排布局
    if industry_blocks:
        st.markdown("#### 🏭 行业提示词块")
        
        # 将行业块分组，确保每行都有固定数量的列
        industry_block_items = list(industry_blocks.items())
        for i in range(0, len(industry_block_items), blocks_per_row):
            row_blocks = industry_block_items[i:i + blocks_per_row]
            
            # 创建固定数量的列，确保对齐
            cols = st.columns(blocks_per_row)
            
            for j in range(blocks_per_row):
                with cols[j]:
                    if j < len(row_blocks):
                        # 有块的行
                        block_id, block = row_blocks[j]
                        is_selected = block_id in selected_blocks
                        if st.checkbox(
                            f"🏭 {block['name']}", 
                            value=is_selected,
                            key=f"industry_{block_id}",
                            help=block.get('description', ''),
                            label_visibility="collapsed"
                        ):
                            selected_industry.append(block_id)
                        
                        # 显示描述提示
                        if block.get('description'):
                            desc = block['description']
                            if len(desc) > 25:
                                st.caption(desc[:25] + "...")
                            else:
                                st.caption(desc)
                    else:
                        # 空列，保持对齐
                        st.write("")
    
    # 如果没有块，显示提示
    if not public_blocks and not industry_blocks:
        st.info("暂无可用的提示词块")
    
    return selected_public + selected_industry

def render_custom_blocks_management(custom_blocks: Dict, 
                                  on_add: Callable = None, 
                                  on_edit: Callable = None, 
                                  on_delete: Callable = None) -> Dict:
    """
    渲染自定义块管理界面
    
    Args:
        custom_blocks: 自定义块字典
        on_add: 添加回调函数
        on_edit: 编辑回调函数
        on_delete: 删除回调函数
    
    Returns:
        更新后的自定义块字典
    """
    st.markdown("#### ✨ 自定义提示词块")
    
    # 添加新自定义块
    with st.expander("➕ 添加自定义块", expanded=False):
        st.markdown("**创建新的自定义提示词块**")
        
        col1, col2 = st.columns(2)
        with col1:
            new_block_key = st.text_input(
                "块键名", 
                placeholder="例如: channel_identity",
                help="用于标识这个块的唯一键名，建议使用英文",
                key=f"new_block_key_{id(custom_blocks)}"
            )
            new_block_name = st.text_input(
                "块名称", 
                placeholder="例如: 频道人设",
                help="显示给用户看的友好名称",
                key=f"new_block_name_{id(custom_blocks)}"
            )
        
        with col2:
            new_block_content = st.text_area(
                "块内容", 
                placeholder="输入自定义内容...\n例如：\n你是一个专业的AI内容创作者，擅长...",
                height=120,
                help="输入这个提示词块的具体内容",
                key=f"new_block_content_{id(custom_blocks)}"
            )
        
        if st.button("➕ 添加自定义块", key=f"add_custom_block_{id(custom_blocks)}"):
            if new_block_key and new_block_name and new_block_content:
                if new_block_key in custom_blocks:
                    st.error(f"❌ 键名 '{new_block_key}' 已存在，请使用不同的键名")
                else:
                    custom_blocks[new_block_key] = {
                        "name": new_block_name,
                        "content": new_block_content
                    }
                    st.success(f"✅ 自定义块 '{new_block_name}' 已添加")
                    if on_add:
                        on_add(custom_blocks)
                    st.rerun()
            else:
                st.warning("⚠️ 请填写完整的块信息")
    
    # 显示现有自定义块
    if custom_blocks:
        st.markdown("**📋 当前自定义块：**")
        
        for key, block in custom_blocks.items():
            col_name, col_content, col_actions = st.columns([1, 2, 1])
            
            with col_name:
                st.write(f"**{block['name']}**")
            
            with col_content:
                st.write(block['content'][:50] + "..." if len(block['content']) > 50 else block['content'])
            
            with col_actions:
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button("✏️", key=f"edit_custom_{key}", help="编辑"):
                        if on_edit:
                            on_edit(key, block)
                
                with col_delete:
                    if st.button("🗑️", key=f"delete_custom_{key}", help="删除"):
                        if on_delete:
                            on_delete(key, custom_blocks)
    
    return custom_blocks

def render_json_preview(json_data: str, title: str = "JSON预览") -> None:
    """
    渲染JSON预览
    
    Args:
        json_data: JSON字符串
        title: 预览标题
    """
    st.markdown(f"### 📝 {title}")
    st.markdown("**JSON格式：**")
    st.code(json_data, language="json")
    
    # 操作按钮
    if st.button("📋 复制JSON", use_container_width=True):
        st.write("✅ JSON已复制到剪贴板")
    
    st.download_button(
        label="💾 下载JSON",
        data=json_data,
        file_name=f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )
