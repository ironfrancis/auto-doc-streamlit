import sys
import os
import json
import datetime
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading

# 使用简化路径管理
from simple_paths import *

import streamlit as st
from language_manager import init_language, get_text, get_language
# Using simple_paths for path management - get_static_dir, get_md_review_dir, get_json_data_dir are already imported
import requests
from core.utils.theme_loader import load_anthropic_theme
from core.utils.icon_library import get_icon

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

# 加载主题
load_anthropic_theme()

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
        st.error(f"频道配置文件格式错误: {e}")
        channels = []
    except Exception as e:
        st.error(f"加载频道配置失败: {e}")
        channels = []
else:
    st.error(f"频道配置文件不存在: {CHANNELS_PATH}")
    channels = []

# 现在所有频道都使用统一的扁平结构
channel_names = [c.get("name", f'频道 {idx}') for idx, c in enumerate(channels)] if channels else []
# 频道和端点选择同一行（改为三列）
sel_col1, sel_col2, sel_col3 = st.columns([1, 1, 1])

with sel_col1:
    selected_channel = st.selectbox(get_text("select_channel"), ["-"] + channel_names, key="channel_selector")

# 获取频道对象（现在统一使用扁平结构）
channel_obj = next((c for c in channels if c.get("name") == selected_channel), None)

# 读取LLM端点
if os.path.exists(ENDPOINTS_PATH):
    with open(ENDPOINTS_PATH, "r", encoding="utf-8") as f:
        endpoints = json.load(f)
else:
    endpoints = []

endpoint_names = [ep["name"] for ep in endpoints] if endpoints else []

with sel_col2:
    # 联动：频道指定端点优先选中
    if endpoint_names:
        if channel_obj and channel_obj.get("llm_endpoint") in endpoint_names:
            endpoint_index = endpoint_names.index(channel_obj["llm_endpoint"])
        else:
            endpoint_index = 0
        selected_endpoint = st.selectbox("选择LLM端点", endpoint_names, index=endpoint_index, key="endpoint_selector")
    else:
        st.error(f"没有找到可用的LLM端点")
        selected_endpoint = ""

with sel_col3:
    # 并发端点多选框
    if endpoint_names:
        # 获取频道绑定的并发端点列表
        default_concurrent_endpoints = []
        if channel_obj:
            concurrent_endpoints_config = channel_obj.get("concurrent_endpoints", [])
            # 只选择在当前可用端点列表中的端点
            default_concurrent_endpoints = [ep for ep in concurrent_endpoints_config if ep in endpoint_names]
        
        selected_concurrent_endpoints = st.multiselect(
            "并发端点（多选）",
            endpoint_names,
            default=default_concurrent_endpoints,
            key="concurrent_endpoints_selector",
            help="选择多个端点进行并发转写"
        )
        
        # 显示已选择数量
        if selected_concurrent_endpoints:
            st.caption(f"已选择 {len(selected_concurrent_endpoints)} 个端点")
    else:
        selected_concurrent_endpoints = []

# 输入区堆叠
md_input = st.text_area("Markdown", height=200, key="md_input_1_Creation")
text_input = st.text_area("Text", height=100, key="text_input_1_Creation")
link_input = st.text_area("Link", height=60, key="link_input_1_Creation")

# AI转写按钮 - 美化样式
st.markdown("""
<style>
    /* 转写按钮区域样式 */
    .transcribe-section {
        margin: 30px 0 20px 0;
        padding: 20px;
        background: linear-gradient(135deg, #FAFAF8 0%, #F5F1E8 100%);
        border-radius: 16px;
        border: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    /* 自定义转写按钮样式 - 使用更强的选择器 */
    div[data-testid="stButton"] > button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #E8957B 0%, #D97A5E 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 24px 56px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 12px rgba(233, 149, 123, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        height: auto !important;
        cursor: pointer !important;
        position: relative !important;
        overflow: hidden !important;
        min-height: 60px !important;
        max-height: none !important;
    }
    
    /* 确保按钮内部的内容也统一 */
    button[data-testid="stBaseButton-primary"] div[data-testid="stMarkdownContainer"],
    button[data-testid="stBaseButton-primary"] div[data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 24px rgba(233, 149, 123, 0.45) !important;
        background: linear-gradient(135deg, #D97A5E 0%, #C86A4E 100%) !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:active,
    button[data-testid="stBaseButton-primary"]:active {
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(233, 149, 123, 0.35) !important;
    }
    
    /* 按钮图标样式 */
    div[data-testid="stButton"] > button[kind="primary"] svg,
    button[data-testid="stBaseButton-primary"] svg {
        vertical-align: middle !important;
        margin-right: 8px !important;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1)) !important;
    }
    
    /* 禁用状态样式 - 保持相同的尺寸 */
    div[data-testid="stButton"] > button[kind="primary"]:disabled,
    button[data-testid="stBaseButton-primary"]:disabled {
        background: linear-gradient(135deg, #D4C5B0 0%, #C4B19D 100%) !important;
        cursor: not-allowed !important;
        opacity: 0.65 !important;
        transform: none !important;
        /* 确保禁用状态下尺寸不变 */
        padding: 24px 56px !important;
        min-height: 60px !important;
        max-height: none !important;
        height: auto !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# 创建按钮容器（两个按钮并排）
col_left, col_btn1, col_btn2, col_right = st.columns([1, 1.2, 1.2, 1])

with col_btn1:
    # 普通AI转写按钮
    button_label = "AI转写"
    transcribe_clicked = st.button(button_label, key="transcribe_main_button", type="primary", use_container_width=True)

with col_btn2:
    # 并发转写按钮
    concurrent_transcribe_clicked = st.button(
        "并发转写", 
        key="concurrent_transcribe_button", 
        type="primary", 
        use_container_width=True,
        disabled=(not selected_concurrent_endpoints),  # 如果没有选择并发端点则禁用
        help="使用多个端点同时进行转写" if selected_concurrent_endpoints else "请先在右侧选择并发端点"
    )

# 按钮下方添加留白
st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# 核心抽象函数：统一的 LLM 端点调用
# ============================================================================

def call_single_llm_endpoint(endpoint_config, prompt, timeout=180):
    """
    统一的 LLM 端点调用函数
    
    参数:
        endpoint_config: 端点配置字典
        prompt: 提示词内容
        timeout: 超时时间（秒）
    
    返回:
        (success: bool, result: str, elapsed_time: float)
        - success: 是否成功
        - result: 成功时返回 markdown 内容，失败时返回错误信息
        - elapsed_time: 请求耗时（秒）
    """
    start_time = time.time()
    
    try:
        api_type = endpoint_config.get("api_type", "")
        api_url = endpoint_config.get("api_url", "").strip()
        api_key = endpoint_config.get("api_key", "")
        model = endpoint_config.get("model", "")
        is_openai = endpoint_config.get("is_openai_compatible", False)
        temperature = endpoint_config.get("temperature", 0.7)
        
        # 根据 API 类型构建请求
        if is_openai:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
            resp = requests.post(api_url, headers=headers, json=data, timeout=timeout)
            
        elif api_type == "Magic":
            # Magic API 支持两种格式
            if "api/chat" in api_url:
                # 新版本 Magic API
                headers = {"api-key": api_key, "Content-Type": "application/json"}
                data = {
                    "message": prompt,
                    "conversation_id": "",
                    "model": model if model else "magic-chat"
                }
            else:
                # 旧版本 Magic API (OpenAI 兼容)
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                data = {
                    "model": model if model else "magic-chat",
                    "messages": [
                        {"role": "system", "content": "你是一个专业的AI写作助手。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature,
                    "stream": False,
                    "max_tokens": 4000
                }
            resp = requests.post(api_url, headers=headers, json=data, timeout=timeout)
        else:
            elapsed = time.time() - start_time
            return (False, f"不支持的 API 类型: {api_type}", elapsed)
        
        elapsed = time.time() - start_time
        
        # 解析响应
        if resp.status_code == 200:
            try:
                result = resp.json()
                # 尝试解析 Magic API 格式
                if "data" in result and "messages" in result["data"] and result["data"]["messages"]:
                    md_result = result["data"]["messages"][0]["message"]["content"]
                # 尝试解析 OpenAI 格式
                else:
                    md_result = result["choices"][0]["message"]["content"]
                return (True, md_result, elapsed)
            except Exception as e:
                return (False, f"解析响应失败: {str(e)}\n响应内容: {resp.text[:200]}", elapsed)
        else:
            return (False, f"HTTP {resp.status_code}: {resp.text[:200]}", elapsed)
    
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        return (False, f"请求超时（{timeout}秒）", elapsed)
    except requests.exceptions.ConnectionError:
        elapsed = time.time() - start_time
        return (False, "连接失败，请检查网络或 API 地址", elapsed)
    except requests.exceptions.RequestException as e:
        elapsed = time.time() - start_time
        return (False, f"请求异常: {str(e)}", elapsed)
    except Exception as e:
        elapsed = time.time() - start_time
        return (False, f"未知错误: {str(e)}", elapsed)


def extract_input_content(md_input, text_input, link_input):
    """
    从输入框提取和整合内容
    
    参数:
        md_input: Markdown 输入
        text_input: 文本输入
        link_input: 链接输入
    
    返回:
        整合后的输入内容字符串
    """
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
    return "\n\n".join(input_parts)


def build_full_prompt(channel_obj, selected_channel, input_content):
    """
    构建完整的提示词
    
    参数:
        channel_obj: 频道对象
        selected_channel: 选中的频道名称
        input_content: 输入内容
    
    返回:
        完整的提示词字符串
    """
    prompt_parts = [f"# 频道信息\n频道：{selected_channel}"]
    
    # 添加频道描述
    channel_description = channel_obj.get("description", "") if channel_obj else ""
    if channel_description:
        prompt_parts.append(f"# 频道描述\n{channel_description}")
    
    # 添加当前时间
    current_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M")
    prompt_parts.append(f"# 当前时间\n现在是：{current_time}")
    
    # 添加内容规则
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
    
    # 添加处理内容
    prompt_parts.append(f"# 处理内容\n{input_content}")
    
    return "\n\n".join(prompt_parts)

# ============================================================================
# 普通转写逻辑（使用抽象函数）
# ============================================================================

if transcribe_clicked:
    if not (md_input.strip() or text_input.strip() or link_input.strip()):
        st.warning("请至少输入一项内容！" if get_language()=="zh" else "Please input at least one field!")
    else:
        # 提取输入内容（使用抽象函数）
        input_content = extract_input_content(md_input, text_input, link_input)
        
        # 构建完整的提示词（使用抽象函数）
        full_prompt = build_full_prompt(channel_obj, selected_channel, input_content)
        
        # 读取端点配置
        ep = next((e for e in endpoints if e["name"] == selected_endpoint), None)
        if not ep:
            st.error("未找到所选LLM端点配置！")
        else:
            # 显示请求状态
            with st.spinner(f"正在请求 {selected_endpoint}...（最长等待180秒）"):
                # 调用统一的端点函数
                success, result, elapsed = call_single_llm_endpoint(ep, full_prompt, timeout=180)
            
            if success:
                # 转写成功
                md_result = result
                st.session_state["ai_md_result"] = md_result
                md_path = os.path.join(STATIC_DIR, "preview.md")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(md_result)
                
                # 保存历史
                save_transcribe_history(selected_channel, "single", input_content, md_result, 
                                      extra={"endpoint": selected_endpoint, "elapsed": elapsed})
                
                # 保存到本地md_review目录
                from datetime import datetime
                safe_channel = selected_channel.replace("/", "_").replace(" ", "_")
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                md_review_dir = get_md_review_dir()
                os.makedirs(md_review_dir, exist_ok=True)
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
                st.info(f"⏱️ 耗时: {elapsed:.2f}秒")
                
                # 延迟一下再刷新，确保文件写入完成
                time.sleep(0.5)
                st.rerun()
            else:
                # 转写失败
                st.error(f"❌ AI转写失败\n\n**错误信息:** {result}\n\n**端点:** {selected_endpoint}\n**耗时:** {elapsed:.2f}秒")

# ============================================================================
# 并发转写包装器函数
# ============================================================================

def concurrent_call_wrapper(endpoint_name, endpoint_config, prompt, timeout=180):
    """
    并发调用的包装器函数
    调用核心的 call_single_llm_endpoint 函数，并返回带端点名称的结果
    
    参数:
        endpoint_name: 端点名称
        endpoint_config: 端点配置字典
        prompt: 提示词内容
        timeout: 超时时间（秒）
    
    返回:
        (endpoint_name, success, result, elapsed_time)
    """
    success, result, elapsed = call_single_llm_endpoint(endpoint_config, prompt, timeout)
    return (endpoint_name, success, result, elapsed)

# ============================================================================
# 并发转写逻辑（使用抽象函数）
# ============================================================================

if concurrent_transcribe_clicked:
    if not (md_input.strip() or text_input.strip() or link_input.strip()):
        st.warning("请至少输入一项内容！" if get_language()=="zh" else "Please input at least one field!")
    elif not selected_concurrent_endpoints:
        st.error("请先选择并发端点！")
    else:
        st.markdown("### ⚡ 并发转写进行中...")
        
        # 提取输入内容（使用抽象函数）
        input_content = extract_input_content(md_input, text_input, link_input)
        
        # 构建完整的提示词（使用抽象函数）
        full_prompt = build_full_prompt(channel_obj, selected_channel, input_content)
        
        # 准备端点配置
        endpoint_configs = {}
        for ep_name in selected_concurrent_endpoints:
            ep = next((e for e in endpoints if e["name"] == ep_name), None)
            if ep:
                endpoint_configs[ep_name] = ep
        
        if not endpoint_configs:
            st.error("未找到任何有效的端点配置！")
        else:
            # 显示并发信息
            st.info(f"🚀 正在并发调用 {len(endpoint_configs)} 个端点...")
            
            # 创建进度显示
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 创建结果容器
            results = {}
            completed_count = 0
            
            # 使用线程池执行并发请求
            with ThreadPoolExecutor(max_workers=len(endpoint_configs)) as executor:
                # 提交所有任务
                future_to_endpoint = {
                    executor.submit(concurrent_call_wrapper, ep_name, ep_config, full_prompt): ep_name
                    for ep_name, ep_config in endpoint_configs.items()
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_endpoint):
                    endpoint_name, success, result, elapsed = future.result()
                    results[endpoint_name] = {
                        "success": success,
                        "result": result,
                        "elapsed": elapsed
                    }
                    
                    completed_count += 1
                    progress = completed_count / len(endpoint_configs)
                    progress_bar.progress(progress)
                    status_text.text(f"已完成: {completed_count}/{len(endpoint_configs)} 个端点")
            
            # 完成后清除进度显示
            progress_bar.empty()
            status_text.empty()
            
            # 统计结果
            success_count = sum(1 for r in results.values() if r["success"])
            failed_count = len(results) - success_count
            
            # 显示统计信息
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("总端点数", len(results))
            with col_stat2:
                st.metric("成功", success_count, delta=success_count, delta_color="normal")
            with col_stat3:
                st.metric("失败", failed_count, delta=failed_count if failed_count > 0 else None, delta_color="inverse")
            
            st.markdown("---")
            
            # 显示结果对比
            st.markdown("### 📊 转写结果对比")
            
            # 为每个结果创建一个可展开的区域
            for ep_name, result_data in results.items():
                status_icon = "✅" if result_data["success"] else "❌"
                elapsed_time = f"{result_data['elapsed']:.2f}秒"
                
                with st.expander(f"{status_icon} {ep_name} ({elapsed_time})", expanded=result_data["success"]):
                    if result_data["success"]:
                        # 显示成功的转写结果
                        st.markdown("**转写结果:**")
                        st.markdown(result_data["result"])
                        
                        # 添加保存按钮
                        if st.button(f"💾 保存此结果", key=f"save_{ep_name}"):
                            # 保存逻辑（与普通转写相同）
                            safe_channel = selected_channel.replace("/", "_").replace(" ", "_")
                            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            md_review_dir = get_md_review_dir()
                            os.makedirs(md_review_dir, exist_ok=True)
                            safe_endpoint = ep_name.replace("/", "_").replace(" ", "_").replace(":", "_")
                            local_md_path = os.path.join(md_review_dir, f"{ts}_{safe_channel}_{safe_endpoint}.md")
                            
                            with open(local_md_path, "w", encoding="utf-8") as f:
                                f.write(result_data["result"])
                            
                            # 保存历史
                            save_transcribe_history(selected_channel, "concurrent_multi", input_content, result_data["result"], 
                                                   extra={"endpoint": ep_name, "elapsed": result_data["elapsed"]})
                            
                            # 尝试用Typora打开
                            try:
                                subprocess.Popen(["open", "-a", "Typora", local_md_path])
                            except Exception:
                                pass
                            
                            st.success(f"✅ 已保存 {ep_name} 的结果！")
                            st.balloons()
                    else:
                        # 显示错误信息
                        st.error(f"**错误:** {result_data['result']}")
            
            # 如果有成功的结果，显示总结
            if success_count > 0:
                st.success(f"🎉 并发转写完成！{success_count} 个端点成功，{failed_count} 个失败。")
            else:
                st.error("😞 所有端点都失败了，请检查配置和网络连接。")

# ============================================================================
# 板块分隔：MD审核与HTML预览
# ============================================================================

# 添加视觉分隔
st.markdown("---")
st.markdown("<br>", unsafe_allow_html=True)

# 导入MD预览所需的模块
from md_utils import md_to_html
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

st.title("📝 MD审核与HTML预览")

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
    
    with st.expander(f"调试信息"):
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

# 初始化变量，避免作用域问题
selected = None
edited = ""
selected_file_data = None

# 页面左右分栏（审核区和预览区用分割线分隔）
col1, col_divider, col2 = st.columns([10, 0.5, 10])

# 在中间列显示分割线
with col_divider:
    st.markdown("""
        <div style="
            width: 1px;
            height: 100vh;
            background: linear-gradient(to bottom, 
                transparent 0%, 
                #E0E0E0 10%, 
                #E0E0E0 90%, 
                transparent 100%);
            margin: 0 auto;
        "></div>
    """, unsafe_allow_html=True)

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
                st.caption(f"最后修改: {datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
                st.caption(f"文件大小: {file_stat.st_size:,} 字节")
                
                # 显示渲染后的Markdown内容
                st.markdown(md_content, unsafe_allow_html=False)
                edited = md_content
            else:
                st.error("无法找到选中的文件")
                edited = ""
    else:
        st.info("暂无Markdown文件")

# 右侧：选择模板、HTML预览
with col2:
    if not md_files:
        st.info("请先在左侧选择Markdown文件")
    else:
        template_files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.html')]
        
        # 从文件名中提取频道信息，自动匹配频道绑定的模板
        default_template_idx = 0
        current_channel_name = None
        matching_channel = None
        
        if selected:
            # 尝试从文件名中解析频道名称（格式：时间戳_频道名_端点名.md）
            import re
            # 匹配格式：20241021_123456_{频道名}_{端点名}.md
            # 使用贪婪匹配，匹配到倒数第二个下划线为止
            # 因为端点名可能包含下划线，所以从后往前找最后一个下划线来分隔
            match = re.match(r'(\d{8}_\d{6})_(.+)\.md$', selected)
            
            safe_channel_name = None
            endpoint_name = None
            
            if match:
                timestamp = match.group(1)
                # 剩余部分（频道名_端点名）
                remaining = match.group(2)
                
                # 尝试匹配所有可能的频道，从最长的开始匹配
                # 这样可以处理频道名和端点名都包含下划线的情况
                best_match_channel = None
                best_match_endpoint = None
                
                for ch in channels:
                    ch_name = ch.get('name', '')
                    # 将频道名转换为safe格式（与保存时的逻辑一致）
                    safe_ch_name = ch_name.replace("/", "_").replace(" ", "_")
                    
                    # 检查 remaining 是否以 safe_ch_name 开头
                    if remaining.startswith(safe_ch_name + "_"):
                        # 提取端点名部分
                        potential_endpoint = remaining[len(safe_ch_name) + 1:]  # +1 跳过下划线
                        
                        # 如果这是目前找到的最佳匹配（频道名最长的）
                        if best_match_channel is None or len(safe_ch_name) > len(best_match_channel.get('name', '').replace("/", "_").replace(" ", "_")):
                            best_match_channel = ch
                            best_match_endpoint = potential_endpoint
                            safe_channel_name = safe_ch_name
                            endpoint_name = potential_endpoint
                
                if best_match_channel:
                    matching_channel = best_match_channel
                    current_channel_name = safe_channel_name
            
            # 如果找到匹配的频道，使用其绑定的模板
            if matching_channel:
                bound_template = matching_channel.get('template', '01_modern_news.html')
                if bound_template in template_files:
                    default_template_idx = template_files.index(bound_template)
        
        # 确保在选择框渲染前有有效的索引
        if default_template_idx >= len(template_files):
            default_template_idx = 0
        
        template_choice = st.selectbox(
            "选择HTML模板", 
            template_files,
            index=default_template_idx,
            key=f"template_selector_{selected}",  # 添加唯一key，确保选择器随文件变化而更新
            help="默认使用频道绑定的模板，也可手动切换"
        )
        
        # 渲染HTML预览
        if selected and edited:
            try:
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
            except Exception as e:
                st.error(f"HTML渲染失败: {str(e)}")
                import traceback
                with st.expander("查看详细错误信息"):
                    st.code(traceback.format_exc())
        else:
            st.info("请选择一个Markdown文件以查看HTML预览") 