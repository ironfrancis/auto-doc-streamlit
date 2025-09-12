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

# 页面配置
st.set_page_config(
    page_title="频道管理",
    layout="wide",
)

# 获取数据目录
def get_channels_file():
    """获取频道配置文件路径"""
    # 使用相对路径，避免复杂的导入
    base_dir = Path(__file__).parent.parent
    channels_file = base_dir / "config" / "channels_v3.json"

    return channels_file

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
    tab1, tab2, tab3 = st.tabs(["📋 频道列表", "➕ 新建频道", "🎨 提示词编辑"])
    
    # 加载频道数据
    channels_list = load_channels()

    # 显示调试信息
    if channels_list:
        st.success(f"✅ 成功加载 {len(channels_list)} 个频道")
        with st.expander("🔍 查看加载详情"):
            st.write("**配置文件路径:**", str(get_channels_file()))
            st.write("**频道列表:**")
            for i, channel in enumerate(channels_list):
                st.write(f"- **{i+1}.** {channel.get('name', '未命名')} (ID: {channel.get('id', '无')})")
    else:
        st.error("❌ 未加载到任何频道数据")
        with st.expander("🔍 调试信息"):
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
                        if st.button("🗑️ 删除", key=f"del_{idx}"):
                            channels_list.pop(idx)
                            if save_channels(channels_list):
                                st.success("删除成功")
                                st.rerun()
                            else:
                                st.error("删除失败")
    
    with tab2:
        # 新建频道
        st.markdown("### 创建新频道")
        
        with st.form("new_channel_form"):
            st.markdown("### 基本信息")
            name = st.text_input("频道名称*", placeholder="输入唯一的频道名称")
            description = st.text_area("频道描述", placeholder="简单描述频道用途", height=100)
            template = st.text_input("HTML模板", value="默认模板")
            llm_endpoint = st.text_input("LLM端点", value="默认端点")
            
            st.markdown("### 角色信息")
            identity = st.text_input("身份", placeholder="例如: 你是XX频道的专业编辑")
            audience = st.text_input("目标受众", placeholder="例如: 互联网行业从业者")
            
            st.markdown("### 任务要求")
            main_goal = st.text_area("主要目标", placeholder="例如: 将复杂技术内容转化为易懂的科普文章")
            
            submitted = st.form_submit_button("创建频道", type="primary")
            
            if submitted:
                if not name:
                    st.error("请输入频道名称")
                elif any(ch.get('basic_info', {}).get('name') == name for ch in channels_list):
                    st.error("频道名称已存在")
                else:
                    new_channel = {
                        "id": name.lower().replace(" ", "_"),
                        "basic_info": {
                            "name": name,
                            "description": description,
                            "template": template,
                            "llm_endpoint": llm_endpoint,
                            "created": datetime.datetime.now().isoformat(),
                            "updated": datetime.datetime.now().isoformat()
                        },
                        "role": {
                            "identity": identity,
                            "audience": audience
                        },
                        "task": {
                            "main_goal": main_goal
                        },
                        "requirements": {
                            "custom_requirements": {}
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
            # 选择要编辑的频道
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
                    submitted = st.form_submit_button("💾 保存提示词设置", type="primary")

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

    # 底部信息
    st.markdown("---")
    st.caption(f"共 {len(channels_list)} 个频道")

if __name__ == "__main__":
    main()
