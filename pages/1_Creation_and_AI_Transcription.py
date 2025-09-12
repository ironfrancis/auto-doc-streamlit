import sys
import os
import json
import datetime
import subprocess
from pathlib import Path

# 使用简化路径管理
from simple_paths import *

import streamlit as st
from language_manager import init_language, get_text, get_language
# Using simple_paths for path management - get_static_dir, get_md_review_dir, get_json_data_dir are already imported
import requests

# 多语言文本定义
T = {
    "zh": {
        "page_title": "AI Content Creation and Transcription",
        "select_channel": "选择频道",
        "transcribe_btn": "AI转写",
        "success": "转写成功！",
        "md_preview": "Markdown预览",
        "md_newtab": "在新标签页中打开"
    },
    "en": {
        "page_title": "AI Content Creation and Transcription",
        "select_channel": "Select Channel",
        "transcribe_btn": "AI Transcribe",
        "success": "Transcription successful!",
        "md_preview": "Markdown Preview",
        "md_newtab": "Open in new tab"
    }
}

HISTORY_PATH = Path(get_json_data_dir()) / "md_transcribe_history.json"

def save_transcribe_history(channel, input_type, input_content, md_result, extra=None):
    record = {
        "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "channel": channel,
        "input_type": input_type,
        "input_content": input_content,
        "md_result": md_result,
        "created_at": datetime.datetime.now().isoformat(),
        "extra": extra or {}
    }
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []
    history.append(record)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# 初始化语言设置
init_language()

st.set_page_config(page_title="AI Transcription", layout="wide")
st.title("Creation and Transcription")

STATIC_DIR = get_static_dir()
# 使用简化路径管理
CHANNELS_PATH = os.path.join(CONFIG_DIR, "channels_v3.json")
ENDPOINTS_PATH = os.path.join(CONFIG_DIR, "llm_endpoints.json")
os.makedirs(STATIC_DIR, exist_ok=True)

# 读取频道
if os.path.exists(CHANNELS_PATH):
    try:
        with open(CHANNELS_PATH, "r", encoding="utf-8") as f:
            channels_data = json.load(f)
            channels = channels_data.get("channels", [])
    except json.JSONDecodeError as e:
        st.error(f"❌ 频道配置文件格式错误: {e}")
        channels = []
    except Exception as e:
        st.error(f"❌ 加载频道配置失败: {e}")
        channels = []
else:
    st.error(f"❌ 频道配置文件不存在: {CHANNELS_PATH}")
    channels = []

# 现在所有频道都使用统一的扁平结构
channel_names = [c.get("name", f'频道 {idx}') for idx, c in enumerate(channels)] if channels else []
# 频道和端点选择同一行
sel_col1, sel_col2 = st.columns([1, 1])

with sel_col1:
    selected_channel = st.selectbox(get_text("select_channel"), ["-"] + channel_names, key="channel_selector")

with sel_col2:
    # 获取频道对象（现在统一使用扁平结构）
    channel_obj = next((c for c in channels if c.get("name") == selected_channel), None)
    
    # 读取LLM端点
    if os.path.exists(ENDPOINTS_PATH):
        with open(ENDPOINTS_PATH, "r", encoding="utf-8") as f:
            endpoints = json.load(f)
    else:
        endpoints = []
    
    endpoint_names = [ep["name"] for ep in endpoints] if endpoints else []
    
    # 联动：频道指定端点优先选中
    if endpoint_names:
        if channel_obj and channel_obj.get("llm_endpoint") in endpoint_names:
            endpoint_index = endpoint_names.index(channel_obj["llm_endpoint"])
        else:
            endpoint_index = 0
        selected_endpoint = st.selectbox("选择LLM端点", endpoint_names, index=endpoint_index, key="endpoint_selector")
    else:
        st.error("❌ 没有找到可用的LLM端点")
        selected_endpoint = ""
    
    # 移除端点配置详情显示

# 移除频道配置信息显示

# 输入区堆叠
md_input = st.text_area("Markdown", height=100, key="md_input_1_Creation")
text_input = st.text_area("Text", height=100, key="text_input_1_Creation")
link_input = st.text_area("Link", height=60, key="link_input_1_Creation")

# AI转写按钮单独一行
if st.button(get_text("transcribe_btn")):
    if not (md_input.strip() or text_input.strip() or link_input.strip()):
        st.warning("请至少输入一项内容！" if get_language()=="zh" else "Please input at least one field!")
    else:
        # 根据有值的输入框拼接内容
        input_parts = []
        if md_input.strip():
            input_parts.append(f"采集到的文章:{md_input.strip()}\n")
        if text_input.strip():
            input_parts.append(f"用户的想法或灵感:{text_input.strip()}\n")
        if link_input.strip():
            try:
                from gzh_url2md import fetch_and_convert_to_md
                md_content = fetch_and_convert_to_md(link_input.strip())
                if md_content:
                    input_parts.append(f"原文链接[Link]\n{link_input.strip()}\n\n解析后的Markdown内容:\n{md_content}")
                else:
                    input_parts.append(f"原文链接[Link]\n{link_input.strip()}\n\n解析失败，请检查链接是否正确")
            except Exception as e:
                input_parts.append(f"原文链接[Link]\n{link_input.strip()}\n\n解析网页内容时出错: {str(e)}")
        input_content = "\n\n".join(input_parts)
        
        # 获取频道描述（现在统一使用扁平结构）
        channel_description = channel_obj.get("description", "") if channel_obj else ""

        # 构建完整的提示词
        prompt_parts = [f"# 频道信息\n频道：{selected_channel}"]

        # 添加频道描述（角色定义）
        if channel_description:
            prompt_parts.append(f"# 频道描述\n{channel_description}")

        # 添加当前时间说明
        current_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M")
        prompt_parts.append(f"# 当前时间\n现在是：{current_time}")

        # 添加内容规则（提示词要求）
        if channel_obj:
            content_rules = channel_obj.get("content_rules", {})
            if content_rules:
                prompt_parts.append("# 内容规范要求")

                # 目标受众
                target_audience = content_rules.get("target_audience", "")
                if target_audience:
                    prompt_parts.append(f"**目标受众:** {target_audience}")

                # 写作风格
                writing_style = content_rules.get("writing_style", {})
                if writing_style:
                    prompt_parts.append("**写作风格要求:**")
                    if writing_style.get("title"):
                        prompt_parts.append(f"- 标题风格: {writing_style['title']}")
                    if writing_style.get("tone"):
                        prompt_parts.append(f"- 写作语气: {writing_style['tone']}")
                    if writing_style.get("depth"):
                        prompt_parts.append(f"- 内容深度: {writing_style['depth']}")

                # 技术规则
                technical_rules = content_rules.get("technical_rules", [])
                if technical_rules:
                    prompt_parts.append("**技术要求:**")
                    for rule in technical_rules:
                        prompt_parts.append(f"- {rule}")
        
        # 添加输入内容
        prompt_parts.append(f"# 处理内容\n{input_content}")
        
        # 组合最终提示词
        full_prompt = "\n\n".join(prompt_parts)
        # 读取端点配置
        ep = next((e for e in endpoints if e["name"] == selected_endpoint), None)
        if not ep:
            st.error("未找到所选LLM端点配置！")
        else:
            api_type = ep.get("api_type", "")
            api_url = ep.get("api_url", "").strip()
            api_key = ep.get("api_key", "")
            model = ep.get("model", "")
            is_openai = ep.get("is_openai_compatible", False)
            temperature = ep.get("temperature", 0.7)
            try:
                # 设置合理的超时时间，支持慢速模型
                timeout = 180  # 延长到180秒，支持慢速模型推理
                
                # 显示请求状态
                with st.spinner(f"正在请求 {selected_endpoint}...（最长等待180秒）"):
                    if is_openai:
                        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                        data = {"model": model, "messages": [{"role": "user", "content": full_prompt}], "temperature": temperature}
                        resp = requests.post(api_url, headers=headers, json=data, timeout=timeout)
                    elif api_type == "Magic":
                        # 优化Magic API请求格式
                        if "api/chat" in api_url:
                            # 新版本Magic API
                            headers = {"api-key": api_key, "Content-Type": "application/json"}
                            data = {
                                "message": full_prompt,
                                "conversation_id": "",
                                "model": model if model else "magic-chat"
                            }
                        else:
                            # 旧版本Magic API (OpenAI兼容)
                            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                            data = {
                                "model": model if model else "magic-chat",
                                "messages": [
                                    {"role": "system", "content": "你是一个专业的AI写作助手。"},
                                    {"role": "user", "content": full_prompt}
                                ],
                                "temperature": temperature,
                                "stream": False,
                                "max_tokens": 4000  # 限制token数量提高速度
                            }
                        
                        resp = requests.post(api_url, headers=headers, json=data, timeout=timeout)
                    else:
                        st.error("暂不支持该API类型")
                        resp = None
                if resp is not None:
                    if resp.status_code == 200:
                        try:
                            result = resp.json()
                            if "data" in result and "messages" in result["data"] and result["data"]["messages"]:
                                md_result = result["data"]["messages"][0]["message"]["content"]
                            else:
                                md_result = result["choices"][0]["message"]["content"]
                        except Exception:
                            md_result = resp.text
                        st.session_state["ai_md_result"] = md_result
                        md_path = os.path.join(STATIC_DIR, "preview.md")
                        with open(md_path, "w", encoding="utf-8") as f:
                            f.write(md_result)
                        # 保存历史
                        save_transcribe_history(selected_channel, "multi", input_content, md_result)
                        # 额外保存到本地md_review目录
                        from datetime import datetime
                        safe_channel = selected_channel.replace("/", "_").replace(" ", "_")
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        md_review_dir = get_md_review_dir()  # 使用统一的路径管理
                        os.makedirs(md_review_dir, exist_ok=True)
                        # 在文件名中加入模型端点名
                        safe_endpoint = selected_endpoint.replace("/", "_").replace(" ", "_").replace(":", "_")
                        local_md_path = os.path.join(md_review_dir, f"{ts}_{safe_channel}_{safe_endpoint}.md")
                        with open(local_md_path, "w", encoding="utf-8") as f:
                            f.write(md_result)
                        # 用Typora打开
                        try:
                            subprocess.Popen(["open", "-a", "Typora", local_md_path])
                        except Exception as e:
                            st.info(f"无法自动打开Typora: {e}")
                        st.success(get_text("success"))
                        
                        # 自动切换到新生成的文章预览
                        new_article_name = f"{ts}_{safe_channel}.md"
                        st.session_state["current_md_file"] = new_article_name
                        st.session_state["current_md_path"] = local_md_path
                        
                        # 显示成功信息和预览提示
                        st.success(f"✅ 转写成功！文章已保存为: {new_article_name}")
                        st.info(f"🔄 正在切换到新文章预览...")
                        
                        # 延迟一下再刷新，确保文件写入完成
                        import time
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"AI转写失败: {resp.text}")
            except requests.exceptions.Timeout:
                st.error(f"⏰ 请求超时！{selected_endpoint} 在180秒内没有响应。建议：\n1. 检查网络连接\n2. 尝试其他LLM端点\n3. 减少输入内容长度\n4. 考虑使用更快的模型")
            except requests.exceptions.ConnectionError:
                st.error(f"🔌 连接失败！无法连接到 {selected_endpoint}。请检查：\n1. API地址是否正确\n2. 网络是否正常\n3. 服务是否可用")
            except requests.exceptions.RequestException as e:
                st.error(f"📡 请求异常：{str(e)}")
            except Exception as e:
                st.error(f"❌ 未知错误：{str(e)}")

import sys
import os

# 路径已在文件开头设置，无需重复

import streamlit as st
from language_manager import init_language, get_text
from md_utils import md_to_html
# Using simple_paths for path management - functions already imported
import streamlit.components.v1 as components
from datetime import datetime

# 多语言文本
T = {
    "zh": {
        "page_title": "本地MD审核与HTML预览",
        "select_md": "选择Markdown文件：",
        "edit": "编辑Markdown内容：",
        "select_template": "选择HTML模板",
        "font_size": "Markdown字号（px）",
        "html_height": "HTML预览高度（px）",
        "html_preview": "HTML预览",
        "get_language()": "语言",
    }
}

# 移除顶部语言选择相关代码

# st.set_page_config(page_title="本地MD审核", layout="wide")
st.title("MD审核与HTML预览")

# 读取所有md文件（包括workspace和legacy目录）
def get_all_md_files():
    """获取所有markdown文件，包括workspace和legacy目录"""
    all_files = []
    
    # 使用简化路径管理
    project_root = PROJECT_ROOT
    
    # 从workspace目录读取
    workspace_md_dir = get_md_review_dir()
    if os.path.exists(workspace_md_dir):
        try:
            workspace_files = [f for f in os.listdir(workspace_md_dir) if f.endswith('.md')]
            for f in workspace_files:
                all_files.append({
                    'name': f,
                    'path': os.path.join(workspace_md_dir, f),
                    'source': 'workspace'
                })
        except Exception as e:
            st.warning(f"读取workspace目录失败: {e}")
    
    # 从legacy目录读取
    legacy_md_dir = os.path.join(project_root, "app", "md_review")
    if os.path.exists(legacy_md_dir):
        try:
            legacy_files = [f for f in os.listdir(legacy_md_dir) if f.endswith('.md')]
            for f in legacy_files:
                # 避免重复文件名
                if not any(item['name'] == f for item in all_files):
                    all_files.append({
                        'name': f,
                        'path': os.path.join(legacy_md_dir, f),
                        'source': 'legacy'
                    })
        except Exception as e:
            st.warning(f"读取legacy目录失败: {e}")
    
    # 按修改时间排序，最新的在前面
    try:
        all_files.sort(key=lambda x: os.path.getmtime(x['path']), reverse=True)
    except Exception as e:
        st.warning(f"文件排序失败: {e}")
    
    return all_files

# 获取所有markdown文件
md_files_data = get_all_md_files()
md_files = [f['name'] for f in md_files_data]


# 显示文件统计信息
if md_files_data:
    workspace_count = len([f for f in md_files_data if f['source'] == 'workspace'])
    legacy_count = len([f for f in md_files_data if f['source'] == 'legacy'])
    
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("总文件数", len(md_files_data))
    with col_stats2:
        st.metric("Workspace目录", workspace_count, delta=f"+{workspace_count}")
    with col_stats3:
        st.metric("Legacy目录", legacy_count, delta=f"+{legacy_count}")
    
    # 显示目录路径信息
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))
else:
    st.warning("未找到任何Markdown文件")
    
    # 显示调试信息
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))
    
    with st.expander("🔍 调试信息"):
        st.write("**检查的目录:**")
        workspace_md_dir = get_md_review_dir()
        legacy_md_dir = os.path.join(project_root, "app", "md_review")
        
        st.write(f"1. Workspace目录: {workspace_md_dir}")
        st.write(f"   - 存在: {os.path.exists(workspace_md_dir)}")
        if os.path.exists(workspace_md_dir):
            try:
                files = os.listdir(workspace_md_dir)
                md_files = [f for f in files if f.endswith('.md')]
                st.write(f"   - 总文件数: {len(files)}")
                st.write(f"   - MD文件数: {len(md_files)}")
            except Exception as e:
                st.error(f"   - 读取失败: {e}")
        
        st.write(f"2. Legacy目录: {legacy_md_dir}")
        st.write(f"   - 存在: {os.path.exists(legacy_md_dir)}")
        if os.path.exists(legacy_md_dir):
            try:
                files = os.listdir(legacy_md_dir)
                md_files = [f for f in files if f.endswith('.md')]
                st.write(f"   - MD文件数: {len(md_files)}")
            except Exception as e:
                st.error(f"   - 读取失败: {e}")

# 路径配置
STATIC_DIR = get_static_dir()
TEMPLATE_DIR = "static/templates"
MD_DIR = get_md_review_dir()
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(MD_DIR, exist_ok=True)

# 页面左右分栏
col1, col2 = st.columns([1, 1])

# 左侧：选择/编辑/预览Markdown
with col1:
    if md_files:
        selected = st.selectbox("选择Markdown文件：", md_files)
        if selected:
            # 找到对应的文件数据
            selected_file_data = next((f for f in md_files_data if f['name'] == selected), None)
        
        if selected_file_data:
            
            # 读取文件内容
            with open(selected_file_data['path'], 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # 显示文件信息
            file_stat = os.stat(selected_file_data['path'])
            st.caption(f"📅 最后修改: {datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
            st.caption(f"📏 文件大小: {file_stat.st_size:,} 字节")
            
            # 显示渲染后的Markdown内容
            st.markdown(md_content, unsafe_allow_html=False)
            edited = md_content
        else:
            st.error("无法找到选中的文件")
            edited = ""
    else:
        edited = ""

# 右侧：选择模板、HTML预览
with col2:
    template_files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.html')]
    template_choice = st.selectbox("选择HTML模板", template_files)
    # 移除html_height滑块
    if selected:
        html_result = md_to_html(edited, template_name=template_choice)
        # 强制覆盖所有容器的高度和overflow，确保完整显示
        force_css = '''
        <style>
        html, body, .container, .main-title, .content, .logo-badge {
            min-height: 100vh !important;
            height: auto !important;
            max-height: none !important;
            overflow: visible !important;
        }
        * { box-sizing: border-box !important; }
        </style>
        '''
        html_result = force_css + html_result
        st.markdown("**HTML预览**", unsafe_allow_html=True)
        # height设为10000，保证内容完整显示且无滚动条
        components.html(html_result, height=10000, scrolling=False) 