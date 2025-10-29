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
import datetime
import time
from core.utils.theme_loader import load_anthropic_theme
from core.utils.icon_library import get_icon

# 页面配置
st.set_page_config(
    page_title="频道管理",
    layout="wide",
)

# 加载主题
load_anthropic_theme()

# 获取数据目录
def get_channels_file():
    """获取频道配置文件路径"""
    # 使用简化路径管理
    from simple_paths import CONFIG_DIR
    channels_file = CONFIG_DIR / "channels_v3.json"

    return channels_file

def load_templates():
    """加载可用的HTML模板文件"""
    try:
        from simple_paths import get_static_dir
        templates_dir = Path(get_static_dir()) / "templates"
        
        if not templates_dir.exists():
            st.warning(f"模板目录不存在: {templates_dir}")
            return []
        
        template_files = [f.name for f in templates_dir.glob("*.html")]
        template_files.sort()  # 按名称排序
        
        if not template_files:
            st.warning("模板目录中没有找到HTML文件")
            return ["01_modern_news.html"]  # 默认模板
        
        return template_files
    except Exception as e:
        st.error(f"加载模板文件失败: {e}")
        return ["01_modern_news.html"]

def load_llm_endpoints():
    """加载可用的LLM端点"""
    try:
        from simple_paths import CONFIG_DIR
        endpoints_file = CONFIG_DIR / "llm_endpoints.json"
        
        if not endpoints_file.exists():
            st.warning(f"LLM端点配置文件不存在: {endpoints_file}")
            return []
        
        with open(endpoints_file, 'r', encoding='utf-8') as f:
            endpoints_data = json.load(f)
        
        if not isinstance(endpoints_data, list):
            st.error("LLM端点配置文件格式错误：应该是数组格式")
            return []
        
        endpoint_names = [ep.get("name", f"端点{i+1}") for i, ep in enumerate(endpoints_data)]
        
        if not endpoint_names:
            st.warning("LLM端点配置文件中没有找到端点")
            return ["Magic gpt4.1"]  # 默认端点
        
        return endpoint_names
    except json.JSONDecodeError as e:
        st.error(f"LLM端点配置文件JSON格式错误: {e}")
        return ["Magic gpt4.1"]
    except Exception as e:
        st.error(f"加载LLM端点失败: {e}")
        return ["Magic gpt4.1"]

def load_channels():
    """加载频道列表"""
    channels_file = get_channels_file()
    if not channels_file.exists():
        st.error(f"频道配置文件不存在: {channels_file}")
        return []

    try:
        with open(channels_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            channels = data.get("channels", [])
            if not channels:
                st.warning("频道配置文件中没有频道数据")
            return channels
    except json.JSONDecodeError as e:
        st.error(f"频道配置文件格式错误: {e}")
        return []
    except Exception as e:
        st.error(f"加载频道配置失败: {e}")
        return []


def save_channels(channels_list):
    """保存频道列表"""
    channels_file = get_channels_file()
    try:
        with open(channels_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data["channels"] = channels_list
        with open(channels_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存失败: {str(e)}")
        return False

def main():
    st.title("📺 频道管理")
    st.markdown("---")
    
    # 选择操作模式
    tab1, tab2, tab3, tab4 = st.tabs(["频道列表", "新建频道", "提示词编辑", "频道配置"])
    
    # 加载频道数据
    channels_list = load_channels()

    # 显示调试信息
    if channels_list:
        st.success(f"成功加载 {len(channels_list)} 个频道")
        with st.expander(f"查看加载详情"):
            st.write("**配置文件路径:**", str(get_channels_file()))
            st.write("**频道列表:**")
            for i, channel in enumerate(channels_list):
                st.write(f"- **{i+1}.** {channel.get('name', '未命名')} (ID: {channel.get('id', '无')})")
    else:
        st.error(f"未加载到任何频道数据")
        with st.expander(f"调试信息"):
            st.write("**配置文件路径:**", str(get_channels_file()))
            st.write("**文件是否存在:**", get_channels_file().exists())
            if get_channels_file().exists():
                try:
                    with open(get_channels_file(), 'r', encoding='utf-8') as f:
                        raw_content = f.read()
                    st.code(raw_content[:500] + ("..." if len(raw_content) > 500 else ""), language="json")
                except Exception as e:
                    st.error(f"读取文件失败: {e}")
    
    with tab1:
        # 频道列表
        if not channels_list:
            st.info("还没有频道，请在 新建频道 标签页创建")
        else:
            for idx, channel in enumerate(channels_list):
                with st.expander(f"**{channel.get('name', '未命名')}**", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**描述:** {channel.get('description', '无')}")
                        st.write(f"**模板:** {channel.get('template', '默认')}")
                        st.write(f"**LLM:** {channel.get('llm_endpoint', '默认')}")
                        
                        content_rules = channel.get('content_rules', {})
                        if content_rules:
                            st.write(f"**受众:** {content_rules.get('target_audience', '无')}")
                            writing_style = content_rules.get('writing_style', {})
                            if writing_style:
                                st.write(f"**标题风格:** {writing_style.get('title', '无')}")
                            
                            technical_rules = content_rules.get('technical_rules', [])
                            if technical_rules:
                                st.write("**内容规则:**")
                                for rule in technical_rules:
                                    st.write(f"- {rule}")
                    
                    with col2:
                        if st.button(f"删除", key=f"del_{idx}"):
                            channels_list.pop(idx)
                            if save_channels(channels_list):
                                st.success("删除成功")
                                st.rerun()
                            else:
                                st.error("删除失败")
    
    with tab2:
        # 新建频道
        st.markdown("### 创建新频道")
        
        # 加载可用的模板和端点
        available_templates = load_templates()
        available_endpoints = load_llm_endpoints()
        
        # 显示加载状态
        if available_templates and available_endpoints:
            st.success(f"已加载 {len(available_templates)} 个模板和 {len(available_endpoints)} 个LLM端点")
            
            # 显示可用选项
            with st.expander(f"查看可用选项", expanded=False):
                col_show_templates, col_show_endpoints = st.columns(2)
                
                with col_show_templates:
                    st.markdown("**可用模板:**")
                    for i, template in enumerate(available_templates):
                        st.write(f"- {template}")
                
                with col_show_endpoints:
                    st.markdown("**可用端点:**")
                    for i, endpoint in enumerate(available_endpoints):
                        st.write(f"- {endpoint}")
        else:
            st.warning(f"部分配置加载失败，将使用默认选项")
        
        with st.form("new_channel_form"):
            st.markdown("### 基本信息")
            name = st.text_input("频道名称*", placeholder="输入唯一的频道名称")
            description = st.text_area("频道描述", placeholder="简单描述频道用途", height=100)
            
            # 使用下拉菜单选择模板和端点
            col_template, col_endpoint = st.columns(2)
            
            with col_template:
                if available_templates:
                    template = st.selectbox(
                        "HTML模板", 
                        available_templates,
                        index=0,
                        help="选择用于渲染文章的HTML模板"
                    )
                else:
                    st.error(f"没有找到可用的HTML模板")
                    template = "01_modern_news.html"  # 默认模板
            
            with col_endpoint:
                if available_endpoints:
                    llm_endpoint = st.selectbox(
                        "LLM端点", 
                        available_endpoints,
                        index=0,
                        help="选择用于AI创作的LLM端点"
                    )
                else:
                    st.error(f"没有找到可用的LLM端点")
                    llm_endpoint = "Magic gpt4.1"  # 默认端点
            
            st.markdown("### 角色信息")
            identity = st.text_input("身份", placeholder="例如: 你是XX频道的专业编辑")
            audience = st.text_input("目标受众", placeholder="例如: 互联网行业从业者")
            
            st.markdown("### 任务要求")
            main_goal = st.text_area("主要目标", placeholder="例如: 将复杂技术内容转化为易懂的科普文章")
            
            submitted = st.form_submit_button("创建频道", type="primary")
            
            if submitted:
                if not name:
                    st.error("请输入频道名称")
                elif any(ch.get('name') == name for ch in channels_list):
                    st.error("频道名称已存在")
                else:
                    # 生成规范的ID（小写+下划线）
                    channel_id = name.lower().replace(" ", "_").replace("（", "_").replace("）", "_").replace("(", "_").replace(")", "_")
                    # 移除连续的下划线
                    import re
                    channel_id = re.sub(r'_+', '_', channel_id).strip('_')
                    
                    # 构建角色描述
                    role_description = ""
                    if identity and audience:
                        role_description = f"{identity}，面向{audience}。"
                    elif identity:
                        role_description = f"{identity}。"
                    elif audience:
                        role_description = f"面向{audience}的专业内容。"
                    
                    # 完整描述
                    full_description = f"{description} {role_description}".strip()
                    
                    new_channel = {
                        "id": channel_id,
                        "created": datetime.datetime.now().isoformat() + "Z",
                        "updated": datetime.datetime.now().isoformat() + "Z",
                        "name": name,
                        "description": full_description,
                        "template": template if template else "01_modern_news.html",
                        "llm_endpoint": llm_endpoint if llm_endpoint else "Magic gpt4.1",
                        "content_rules": {
                            "target_audience": audience or "通用受众",
                            "writing_style": {
                                "title": "吸引读者的标题",
                                "tone": "专业且易懂",
                                "depth": "适度深入"
                            },
                            "technical_rules": [
                                main_goal or "根据输入内容进行专业转写",
                                "保持内容的准确性和可读性",
                                "适当添加个人观点和分析"
                            ]
                        }
                    }
                    
                    channels_list.append(new_channel)
                    if save_channels(channels_list):
                        st.success(f"频道 '{name}' 创建成功！")
                        st.balloons()
                    else:
                        st.error("保存失败")

    with tab3:
        # 提示词编辑
        st.markdown("### 编辑频道提示词")

        if not channels_list:
            st.info("还没有频道，请先创建频道")
        else:
            # 选择要编辑的频道 - 统一使用扁平结构
            channel_names = [ch.get('name', f'频道 {idx}') for idx, ch in enumerate(channels_list)]
            selected_channel_idx = st.selectbox(
                "选择要编辑的频道",
                range(len(channels_list)),
                format_func=lambda x: channel_names[x]
            )

            if selected_channel_idx is not None:
                channel = channels_list[selected_channel_idx]
                channel_id = channel.get('id', f'channel_{selected_channel_idx}')

                st.markdown(f"#### 编辑频道：{channel.get('name', '未命名')}")

                # 显示当前频道信息
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**描述:** {channel.get('description', '无')}")
                    st.write(f"**模板:** {channel.get('template', '默认')}")
                    st.write(f"**LLM:** {channel.get('llm_endpoint', '默认')}")

                with col2:
                    content_rules = channel.get('content_rules', {})
                    if content_rules:
                        st.write(f"**受众:** {content_rules.get('target_audience', '无')}")

                # 编辑表单
                with st.form(f"edit_prompt_{channel_id}"):
                    st.markdown("##### 内容规则设置")

                    # 目标受众
                    target_audience = st.text_input(
                        "目标受众",
                        value=content_rules.get('target_audience', ''),
                        placeholder="例如：互联网行业从业者、AI专业人士"
                    )

                    # 写作风格
                    writing_style = content_rules.get('writing_style', {})

                    col1, col2 = st.columns(2)
                    with col1:
                        title_style = st.text_area(
                            "标题风格要求",
                            value=writing_style.get('title', ''),
                            height=80,
                            placeholder="例如：使用吸引眼球的标题"
                        )

                        writing_tone = st.text_area(
                            "写作语气要求",
                            value=writing_style.get('tone', ''),
                            height=80,
                            placeholder="例如：生动活泼、专业客观"
                        )

                    with col2:
                        content_depth = st.text_area(
                            "内容深度要求",
                            value=writing_style.get('depth', ''),
                            height=80,
                            placeholder="例如：深度分析、循序渐进"
                        )

                    # 技术规则
                    technical_rules = content_rules.get('technical_rules', [])
                    technical_rules_text = '\n'.join(technical_rules) if technical_rules else ''

                    technical_rules_input = st.text_area(
                        "技术规则（每行一条）",
                        value=technical_rules_text,
                        height=120,
                        placeholder="例如：\n保留原文图片链接\n技术内容必须准确\n添加个人观察"
                    )

                    # 提交按钮
                    submitted = st.form_submit_button(f"保存提示词设置", type="primary")

                    if submitted:
                        # 更新频道数据
                        updated_content_rules = {
                            "target_audience": target_audience,
                            "writing_style": {
                                "title": title_style,
                                "tone": writing_tone,
                                "depth": content_depth
                            },
                            "technical_rules": [
                                rule.strip() for rule in technical_rules_input.split('\n')
                                if rule.strip()
                            ]
                        }

                        # 更新频道
                        channels_list[selected_channel_idx]['content_rules'] = updated_content_rules
                        channels_list[selected_channel_idx]['updated'] = datetime.datetime.now().isoformat() + 'Z'

                        if save_channels(channels_list):
                            st.success("提示词设置保存成功！")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("保存失败，请重试")
    
    with tab4:
        # 频道配置编辑
        st.markdown("### 编辑频道配置")
        st.caption("修改频道的模板、LLM端点等基本配置信息")
        
        if not channels_list:
            st.info("还没有频道，请先创建频道")
        else:
            # 选择要编辑的频道
            channel_names = [ch.get('name', f'频道 {idx}') for idx, ch in enumerate(channels_list)]
            selected_config_idx = st.selectbox(
                "选择要配置的频道",
                range(len(channels_list)),
                format_func=lambda x: channel_names[x],
                key="config_channel_selector"
            )
            
            if selected_config_idx is not None:
                channel = channels_list[selected_config_idx]
                channel_id = channel.get('id', f'channel_{selected_config_idx}')
                
                st.markdown(f"#### 配置频道：{channel.get('name', '未命名')}")
                
                # 显示当前配置概览
                with st.expander("📋 当前配置概览", expanded=True):
                    col_overview1, col_overview2 = st.columns(2)
                    with col_overview1:
                        st.write(f"**频道ID:** `{channel.get('id', '无')}`")
                        st.write(f"**频道名称:** {channel.get('name', '无')}")
                        st.write(f"**频道描述:** {channel.get('description', '无')}")
                    with col_overview2:
                        st.write(f"**HTML模板:** `{channel.get('template', '默认')}`")
                        st.write(f"**LLM端点:** `{channel.get('llm_endpoint', '默认')}`")
                        st.write(f"**创建时间:** {channel.get('created', '未知')}")
                
                # 配置编辑表单
                with st.form(f"config_form_{channel_id}"):
                    st.markdown("##### 基本配置")
                    
                    # 频道名称
                    new_name = st.text_input(
                        "频道名称*",
                        value=channel.get('name', ''),
                        help="修改频道名称"
                    )
                    
                    # 频道描述
                    new_description = st.text_area(
                        "频道描述",
                        value=channel.get('description', ''),
                        height=100,
                        help="简单描述频道用途和定位"
                    )
                    
                    st.markdown("##### 模板和端点配置")
                    
                    # 加载可用的模板和端点
                    available_templates = load_templates()
                    available_endpoints = load_llm_endpoints()
                    
                    col_template, col_endpoint = st.columns(2)
                    
                    with col_template:
                        # HTML模板选择
                        current_template = channel.get('template', '01_modern_news.html')
                        if current_template in available_templates:
                            template_idx = available_templates.index(current_template)
                        else:
                            template_idx = 0
                        
                        new_template = st.selectbox(
                            "HTML模板",
                            available_templates,
                            index=template_idx,
                            help="选择用于渲染文章的HTML模板"
                        )
                        
                        # 显示模板预览信息
                        if new_template != current_template:
                            st.info(f"将从 `{current_template}` 更改为 `{new_template}`")
                    
                    with col_endpoint:
                        # LLM端点选择
                        current_endpoint = channel.get('llm_endpoint', 'Magic gpt4.1')
                        if current_endpoint in available_endpoints:
                            endpoint_idx = available_endpoints.index(current_endpoint)
                        else:
                            endpoint_idx = 0
                        
                        new_endpoint = st.selectbox(
                            "LLM端点",
                            available_endpoints,
                            index=endpoint_idx,
                            help="选择用于AI创作的LLM端点"
                        )
                        
                        # 显示端点变更信息
                        if new_endpoint != current_endpoint:
                            st.info(f"将从 `{current_endpoint}` 更改为 `{new_endpoint}`")
                    
                    st.markdown("##### 并发端点配置")
                    st.caption("选择多个端点用于并发转写，可以同时使用不同的模型生成内容")
                    
                    # 并发端点多选框
                    current_concurrent_endpoints = channel.get('concurrent_endpoints', [])
                    # 只显示在可用端点列表中的端点
                    valid_concurrent_endpoints = [ep for ep in current_concurrent_endpoints if ep in available_endpoints]
                    
                    new_concurrent_endpoints = st.multiselect(
                        "并发端点列表",
                        available_endpoints,
                        default=valid_concurrent_endpoints,
                        help="选择多个端点进行并发转写对比"
                    )
                    
                    # 显示并发端点提示
                    if new_concurrent_endpoints:
                        st.success(f"✅ 已选择 {len(new_concurrent_endpoints)} 个并发端点")
                        with st.expander("📋 查看并发端点列表"):
                            for i, ep in enumerate(new_concurrent_endpoints, 1):
                                st.write(f"{i}. {ep}")
                    else:
                        st.info("💡 未选择并发端点，将只使用主端点进行转写")
                    
                    st.markdown("---")
                    
                    # 显示变更摘要
                    changes = []
                    if new_name != channel.get('name', ''):
                        changes.append(f"- 名称: `{channel.get('name', '')}` → `{new_name}`")
                    if new_description != channel.get('description', ''):
                        changes.append(f"- 描述: 已修改")
                    if new_template != channel.get('template', ''):
                        changes.append(f"- 模板: `{channel.get('template', '')}` → `{new_template}`")
                    if new_endpoint != channel.get('llm_endpoint', ''):
                        changes.append(f"- 端点: `{channel.get('llm_endpoint', '')}` → `{new_endpoint}`")
                    if set(new_concurrent_endpoints) != set(current_concurrent_endpoints):
                        changes.append(f"- 并发端点: {len(current_concurrent_endpoints)} 个 → {len(new_concurrent_endpoints)} 个")
                    
                    if changes:
                        st.markdown("**📝 待保存的变更:**")
                        for change in changes:
                            st.markdown(change)
                    else:
                        st.info("暂无变更")
                    
                    # 提交按钮
                    col_submit1, col_submit2 = st.columns([1, 3])
                    with col_submit1:
                        submitted = st.form_submit_button("💾 保存配置", type="primary", use_container_width=True)
                    with col_submit2:
                        if submitted:
                            st.write("")  # 占位
                    
                    if submitted:
                        # 验证输入
                        if not new_name:
                            st.error("❌ 频道名称不能为空")
                        elif new_name != channel.get('name', '') and any(ch.get('name') == new_name for ch in channels_list):
                            st.error(f"❌ 频道名称 '{new_name}' 已存在")
                        else:
                            # 更新频道配置
                            channels_list[selected_config_idx]['name'] = new_name
                            channels_list[selected_config_idx]['description'] = new_description
                            channels_list[selected_config_idx]['template'] = new_template
                            channels_list[selected_config_idx]['llm_endpoint'] = new_endpoint
                            channels_list[selected_config_idx]['concurrent_endpoints'] = new_concurrent_endpoints
                            channels_list[selected_config_idx]['updated'] = datetime.datetime.now().isoformat() + 'Z'
                            
                            # 如果名称改变了，更新ID
                            if new_name != channel.get('name', ''):
                                import re
                                new_id = new_name.lower().replace(" ", "_").replace("（", "_").replace("）", "_").replace("(", "_").replace(")", "_")
                                new_id = re.sub(r'_+', '_', new_id).strip('_')
                                channels_list[selected_config_idx]['id'] = new_id
                            
                            # 保存到文件
                            if save_channels(channels_list):
                                st.success(f"✅ 频道配置保存成功！")
                                if new_concurrent_endpoints:
                                    st.info(f"🔧 已配置 {len(new_concurrent_endpoints)} 个并发端点")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ 保存失败，请重试")

    # 底部信息
    st.markdown("---")
    st.caption(f"共 {len(channels_list)} 个频道")

if __name__ == "__main__":
    main()
