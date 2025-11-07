import sys
import os
import json
import datetime
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
import asyncio
from typing import AsyncIterator, Optional

# 使用简化路径管理
from simple_paths import *

import streamlit as st
from language_manager import init_language, get_text, get_language
# Using simple_paths for path management - get_static_dir, get_md_review_dir, get_json_data_dir are already imported
import requests
try:
    import httpx
except ImportError:
    httpx = None
    st.warning("⚠️ 需要安装 httpx 以支持异步流式输出: pip install httpx")
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

    else:
        selected_concurrent_endpoints = []

# ============================================================================
# 并发历史管理函数
# ============================================================================

def get_concurrent_history_dir():
    """获取并发历史目录"""
    history_dir = os.path.join(get_workspace_dir(), "concurrent_history")
    os.makedirs(history_dir, exist_ok=True)
    return history_dir


def save_concurrent_history(task_id, channel, results, saved_files):
    """
    保存并发转写历史到 JSON 文件
    
    参数:
        task_id: 任务ID（时间戳）
        channel: 频道名称
        results: 结果字典
        saved_files: 保存的文件列表
    """
    history_dir = get_concurrent_history_dir()
    
    # 构建元数据
    metadata = {
        "id": task_id,
        "channel": channel,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "results": []
    }
    
    # 添加每个端点的结果信息（只保存必要信息，不保存内容）
    for ep_name, result_data in results.items():
        result_info = {
            "endpoint": ep_name,
            "success": result_data["success"],
            "elapsed": result_data["elapsed"],
            "file_path": None  # 初始化为 None
        }
        
        # 如果成功，找到对应的文件路径
        if result_data["success"]:
            for saved_ep, saved_path in saved_files:
                if saved_ep == ep_name:
                    result_info["file_path"] = saved_path
                    break
        else:
            # 失败时保存错误信息
            result_info["error"] = result_data["result"]
        
        metadata["results"].append(result_info)
    
    # 统计信息
    success_count = sum(1 for r in results.values() if r["success"])
    metadata["statistics"] = {
        "total": len(results),
        "success": success_count,
        "failed": len(results) - success_count,
        "avg_time": sum(r["elapsed"] for r in results.values()) / len(results) if results else 0
    }
    
    # 保存到 JSON 文件
    json_path = os.path.join(history_dir, f"{task_id}_{channel.replace('/', '_').replace(' ', '_')}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    return json_path


def load_concurrent_history_list():
    """
    加载并发历史记录列表
    
    返回:
        列表，每项包含 (display_name, file_path, metadata)
    """
    history_dir = get_concurrent_history_dir()
    history_files = sorted(
        [f for f in os.listdir(history_dir) if f.endswith('.json')],
        reverse=True  # 最新的在前
    )
    
    history_list = []
    for filename in history_files:
        file_path = os.path.join(history_dir, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            # 构建显示名称
            timestamp = metadata.get("timestamp", "未知时间")
            channel = metadata.get("channel", "未知频道")
            stats = metadata.get("statistics", {})
            total = stats.get("total", 0)
            success = stats.get("success", 0)
            
            display_name = f"{timestamp} | {channel} | {success}/{total} 成功"
            history_list.append((display_name, file_path, metadata))
        except Exception as e:
            # 忽略损坏的文件
            continue
    
    return history_list


def load_concurrent_history(file_path):
    """
    从 JSON 文件加载并发历史
    
    返回:
        metadata 字典
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ============================================================================
# 输入区
# ============================================================================

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

async def call_single_llm_endpoint_stream(endpoint_config, prompt, timeout=180, stream_container=None):
    """
    异步流式 LLM 端点调用函数
    
    参数:
        endpoint_config: 端点配置字典
        prompt: 提示词内容
        timeout: 超时时间（秒）
        stream_container: Streamlit 容器对象，用于实时显示流式输出（可选）
    
    返回:
        (success: bool, result: str, elapsed_time: float)
        - success: 是否成功
        - result: 成功时返回 markdown 内容，失败时返回错误信息
        - elapsed_time: 请求耗时（秒）
    """
    if httpx is None:
        raise ImportError("需要安装 httpx: pip install httpx")
    
    start_time = time.time()
    full_result = ""
    
    try:
        api_type = endpoint_config.get("api_type", "")
        api_url = endpoint_config.get("api_url", "").strip()
        api_key = endpoint_config.get("api_key", "")
        model = endpoint_config.get("model", "")
        is_openai = endpoint_config.get("is_openai_compatible", False)
        temperature = endpoint_config.get("temperature", 0.7)
        
        # 构建请求参数
        if is_openai:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "stream": True  # 启用流式输出
            }
            api_type_flag = "openai"
            
        elif api_type == "Magic":
            # Magic API 支持两种格式
            if "api/chat" in api_url:
                # 新版本 Magic API（不支持流式，需要回退到同步模式）
                elapsed = time.time() - start_time
                raise ValueError("新版本 Magic API 不支持流式输出，请使用同步模式")
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
                    "stream": True,  # 启用流式输出
                    "max_tokens": 4000
                }
                api_type_flag = "magic_openai"
        else:
            elapsed = time.time() - start_time
            return (False, f"不支持的 API 类型: {api_type}", elapsed)
        
        # 使用 httpx 进行异步流式请求
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", api_url, headers=headers, json=data) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    elapsed = time.time() - start_time
                    return (False, f"HTTP {response.status_code}: {error_text[:200].decode('utf-8', errors='ignore')}", elapsed)
                
                # 处理流式响应
                buffer = ""
                async for chunk in response.aiter_bytes():
                    if chunk:
                        buffer += chunk.decode('utf-8', errors='ignore')
                        
                        # 处理 SSE 格式的数据（每行一个 JSON 对象）
                        lines = buffer.split('\n')
                        buffer = lines[-1]  # 保留最后不完整的行
                        
                        for line in lines[:-1]:
                            line = line.strip()
                            if not line or line.startswith(':'):
                                continue
                            
                            # 处理 data: 前缀
                            if line.startswith('data: '):
                                line = line[6:]
                            
                            if line == '[DONE]':
                                continue
                            
                            try:
                                json_data = json.loads(line)
                                
                                # 解析 OpenAI 格式
                                if "choices" in json_data and len(json_data["choices"]) > 0:
                                    delta = json_data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_result += content
                                        if stream_container:
                                            # 实时更新流式输出
                                            stream_container.markdown(full_result)
                                            # 使用异步延迟以确保 UI 更新
                                            await asyncio.sleep(0.01)
                                
                                # 解析 Magic API 格式（如果支持流式）
                                elif "data" in json_data:
                                    # Magic API 流式格式可能不同，需要根据实际情况调整
                                    pass
                                    
                            except json.JSONDecodeError:
                                continue
        
        elapsed = time.time() - start_time
        return (True, full_result, elapsed)
    
    except httpx.TimeoutException:
        elapsed = time.time() - start_time
        return (False, f"请求超时（{timeout}秒）", elapsed)
    except httpx.ConnectError:
        elapsed = time.time() - start_time
        return (False, "连接失败，请检查网络或 API 地址", elapsed)
    except httpx.RequestError as e:
        elapsed = time.time() - start_time
        return (False, f"请求异常: {str(e)}", elapsed)
    except Exception as e:
        elapsed = time.time() - start_time
        return (False, f"未知错误: {str(e)}", elapsed)


def call_single_llm_endpoint(endpoint_config, prompt, timeout=180, use_stream=False, stream_container=None):
    """
    统一的 LLM 端点调用函数（支持同步和异步流式两种模式）
    
    参数:
        endpoint_config: 端点配置字典
        prompt: 提示词内容
        timeout: 超时时间（秒）
        use_stream: 是否使用流式输出（默认 False，保持向后兼容）
        stream_container: Streamlit 容器对象，用于实时显示流式输出（仅当 use_stream=True 时有效）
    
    返回:
        (success: bool, result: str, elapsed_time: float)
        - success: 是否成功
        - result: 成功时返回 markdown 内容，失败时返回错误信息
        - elapsed_time: 请求耗时（秒）
    """
    if use_stream and httpx is not None:
        # 使用异步流式模式
        try:
            # 在 Streamlit 中运行异步函数
            # 尝试获取现有事件循环，如果没有则创建新的
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # 运行异步函数
            result = loop.run_until_complete(
                call_single_llm_endpoint_stream(endpoint_config, prompt, timeout, stream_container)
            )
            return result
        except Exception as e:
            # 如果异步模式失败，回退到同步模式
            st.warning(f"流式输出失败，回退到同步模式: {str(e)}")
    
    # 同步模式（原有逻辑）
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
            # 创建流式输出容器
            stream_container = st.empty()
            stream_container.info(f"🔄 正在连接 {selected_endpoint}...")
            
            # 调用统一的端点函数（启用流式输出）
            success, result, elapsed = call_single_llm_endpoint(
                ep, full_prompt, timeout=180, 
                use_stream=True, 
                stream_container=stream_container
            )
            
            # 清理流式输出容器
            stream_container.empty()
            
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
                # 文件名应该是 {ts}_{safe_channel}_{safe_endpoint}.md
                new_article_name = f"{ts}_{safe_channel}_{safe_endpoint}.md"
                st.session_state["current_md_file"] = new_article_name
                st.session_state["current_md_path"] = local_md_path
                st.session_state["auto_select_triggered"] = True  # 标记已触发自动选择
                
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

async def concurrent_call_wrapper_async(endpoint_name, endpoint_config, prompt, timeout=180, stream_container=None):
    """
    异步并发调用的包装器函数
    直接调用异步流式函数，返回带端点名称的结果
    
    参数:
        endpoint_name: 端点名称
        endpoint_config: 端点配置字典
        prompt: 提示词内容
        timeout: 超时时间（秒）
        stream_container: Streamlit 容器对象，用于实时显示流式输出
    
    返回:
        (endpoint_name, success, result, elapsed_time)
    """
    if httpx is None:
        # 如果 httpx 不可用，回退到同步模式
        success, result, elapsed = call_single_llm_endpoint(endpoint_config, prompt, timeout, use_stream=False)
    else:
        success, result, elapsed = await call_single_llm_endpoint_stream(
            endpoint_config, prompt, timeout, stream_container
        )
    return (endpoint_name, success, result, elapsed)


def concurrent_call_wrapper(endpoint_name, endpoint_config, prompt, timeout=180, use_stream=False, stream_container=None):
    """
    并发调用的包装器函数（同步版本，用于线程池）
    调用核心的 call_single_llm_endpoint 函数，并返回带端点名称的结果
    
    参数:
        endpoint_name: 端点名称
        endpoint_config: 端点配置字典
        prompt: 提示词内容
        timeout: 超时时间（秒）
        use_stream: 是否使用流式输出
        stream_container: Streamlit 容器对象，用于实时显示流式输出
    
    返回:
        (endpoint_name, success, result, elapsed_time)
    """
    success, result, elapsed = call_single_llm_endpoint(
        endpoint_config, prompt, timeout, 
        use_stream=use_stream, 
        stream_container=stream_container
    )
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
            
            # 为每个端点创建独立的流式输出容器
            stream_containers = {}
            for ep_name in endpoint_configs.keys():
                stream_containers[ep_name] = st.empty()
                stream_containers[ep_name].info(f"🔄 正在连接 {ep_name}...")
            
            # 创建结果容器
            results = {}
            saved_files = []
            # 使用字典存储计数器，避免 nonlocal 作用域问题
            counters = {
                "completed_count": 0,
                "success_count": 0,
                "failed_count": 0
            }
            
            # 准备保存目录和基础时间戳
            base_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_channel = selected_channel.replace("/", "_").replace(" ", "_")
            md_review_dir = get_md_review_dir()
            os.makedirs(md_review_dir, exist_ok=True)
            
            # 使用 asyncio 执行并发异步请求（更适合流式输出）
            async def run_concurrent_transcribe():
                """异步执行并发转写"""
                # 创建所有异步任务
                tasks = [
                    concurrent_call_wrapper_async(
                        ep_name,
                        ep_config,
                        full_prompt,
                        180,  # timeout
                        stream_containers[ep_name]  # stream_container
                    )
                    for ep_name, ep_config in endpoint_configs.items()
                ]
                
                # 使用 asyncio.as_completed 来实时处理完成的任务
                completed_tasks = []
                for coro in asyncio.as_completed(tasks):
                    try:
                        result = await coro
                        completed_tasks.append(result)
                        
                        endpoint_name, success, result_text, elapsed = result
                        results[endpoint_name] = {
                            "success": success,
                            "result": result_text,
                            "elapsed": elapsed
                        }
                        
                        # 清理该端点的流式输出容器
                        if endpoint_name in stream_containers:
                            stream_containers[endpoint_name].empty()
                        
                        counters["completed_count"] = len(completed_tasks)
                        
                        # 如果成功，立即保存并打开文件
                        if success:
                            counters["success_count"] += 1
                            # 为每个端点添加序号，避免时间戳冲突
                            ts = f"{base_ts}_{counters['completed_count']}"
                            safe_endpoint = endpoint_name.replace("/", "_").replace(" ", "_").replace(":", "_")
                            local_md_path = os.path.join(md_review_dir, f"{ts}_{safe_channel}_{safe_endpoint}.md")
                            
                            # 保存文件
                            with open(local_md_path, "w", encoding="utf-8") as f:
                                f.write(result_text)
                            
                            # 保存历史
                            save_transcribe_history(selected_channel, "concurrent", input_content, result_text, 
                                                   extra={"endpoint": endpoint_name, "elapsed": elapsed})
                            
                            # 立即打开文件，不等待其他端点
                            try:
                                subprocess.Popen(["open", local_md_path])
                                status_text.text(f"✅ {endpoint_name} 完成并已打开 ({elapsed:.2f}秒) | 进度: {counters['completed_count']}/{len(endpoint_configs)}")
                            except Exception as e:
                                status_text.text(f"✅ {endpoint_name} 完成 ({elapsed:.2f}秒) | 进度: {counters['completed_count']}/{len(endpoint_configs)}")
                            
                            saved_files.append((endpoint_name, local_md_path))
                        else:
                            counters["failed_count"] += 1
                            status_text.text(f"❌ {endpoint_name} 失败 ({elapsed:.2f}秒) | 进度: {counters['completed_count']}/{len(endpoint_configs)}")
                        
                        # 更新进度条
                        progress = counters["completed_count"] / len(endpoint_configs)
                        progress_bar.progress(progress)
                        
                    except Exception as e:
                        st.error(f"处理任务时出错: {str(e)}")
            
            # 运行异步并发转写
            try:
                # 获取或创建事件循环
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # 运行异步函数
                loop.run_until_complete(run_concurrent_transcribe())
            except Exception as e:
                st.error(f"并发转写执行失败: {str(e)}")
                # 如果异步模式失败，回退到线程池模式
                st.warning("异步模式失败，回退到线程池模式...")
                with ThreadPoolExecutor(max_workers=len(endpoint_configs)) as executor:
                    future_to_endpoint = {
                        executor.submit(
                            concurrent_call_wrapper, 
                            ep_name, 
                            ep_config, 
                            full_prompt,
                            180,
                            True,
                            stream_containers[ep_name]
                        ): ep_name
                        for ep_name, ep_config in endpoint_configs.items()
                    }
                    
                    for future in as_completed(future_to_endpoint):
                        endpoint_name, success, result_text, elapsed = future.result()
                        results[endpoint_name] = {
                            "success": success,
                            "result": result_text,
                            "elapsed": elapsed
                        }
                        
                        if endpoint_name in stream_containers:
                            stream_containers[endpoint_name].empty()
                        
                        counters["completed_count"] += 1
                        
                        if success:
                            counters["success_count"] += 1
                            ts = f"{base_ts}_{counters['completed_count']}"
                            safe_endpoint = endpoint_name.replace("/", "_").replace(" ", "_").replace(":", "_")
                            local_md_path = os.path.join(md_review_dir, f"{ts}_{safe_channel}_{safe_endpoint}.md")
                            
                            with open(local_md_path, "w", encoding="utf-8") as f:
                                f.write(result_text)
                            
                            save_transcribe_history(selected_channel, "concurrent", input_content, result_text, 
                                                   extra={"endpoint": endpoint_name, "elapsed": elapsed})
                            
                            try:
                                subprocess.Popen(["open", local_md_path])
                                status_text.text(f"✅ {endpoint_name} 完成并已打开 ({elapsed:.2f}秒) | 进度: {counters['completed_count']}/{len(endpoint_configs)}")
                            except Exception:
                                status_text.text(f"✅ {endpoint_name} 完成 ({elapsed:.2f}秒) | 进度: {counters['completed_count']}/{len(endpoint_configs)}")
                            
                            saved_files.append((endpoint_name, local_md_path))
                        else:
                            counters["failed_count"] += 1
                            status_text.text(f"❌ {endpoint_name} 失败 ({elapsed:.2f}秒) | 进度: {counters['completed_count']}/{len(endpoint_configs)}")
                        
                        progress = counters["completed_count"] / len(endpoint_configs)
                        progress_bar.progress(progress)
                        time.sleep(0.3)
            
            # 完成后清除进度显示
            progress_bar.empty()
            status_text.empty()
            
            # 保存并发历史到 JSON 文件
            save_concurrent_history(base_ts, selected_channel, results, saved_files)
            
            # 保存到 session_state 以便在对比区显示
            st.session_state["current_concurrent_results"] = {
                "task_id": base_ts,
                "channel": selected_channel,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "results": results,
                "saved_files": saved_files,
                "statistics": {
                    "total": len(results),
                    "success": counters["success_count"],
                    "failed": counters["failed_count"]
                }
            }
            
            # 显示最终统计
            if saved_files:
                st.success(f"🎉 并发转写完成！已自动保存并打开 {len(saved_files)} 个成功的结果")
            
            # 显示统计信息
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("总端点数", len(results))
            with col_stat2:
                st.metric("成功", counters["success_count"], delta=counters["success_count"], delta_color="normal")
            with col_stat3:
                st.metric("失败", counters["failed_count"], delta=counters["failed_count"] if counters["failed_count"] > 0 else None, delta_color="inverse")
            
            # 并发转写完成后，自动切换到对比区
            st.session_state["show_concurrent_compare"] = True

# ============================================================================
# 并发结果对比区（独立、可折叠）
# ============================================================================

def render_concurrent_results(results_data, key_prefix="current"):
    """
    渲染并发结果对比
    
    参数:
        results_data: 包含 results 和 saved_files 的字典
        key_prefix: 按钮key的前缀，避免重复
    """
    results = results_data.get("results", {})
    saved_files = results_data.get("saved_files", [])
    
    if not results:
        st.info("暂无并发结果")
        return
    
    # 根据端点数量决定列数（最多4列，最少2列）
    num_endpoints = len(results)
    num_columns = min(max(2, num_endpoints), 4)
    
    # 创建并排的列布局
    result_columns = st.columns(num_columns)
    
    # 将结果分配到各列中
    for idx, (ep_name, result_data) in enumerate(results.items()):
        col_idx = idx % num_columns
        
        with result_columns[col_idx]:
            # 卡片样式的容器
            status_icon = "✅" if result_data["success"] else "❌"
            status_color = "#28a745" if result_data["success"] else "#dc3545"
            elapsed_time = f"{result_data['elapsed']:.2f}秒"
            
            # 使用自定义样式的容器
            st.markdown(f"""
            <div style="
                border: 2px solid {status_color};
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                background-color: rgba(255, 255, 255, 0.05);
            ">
                <h4 style="margin: 0 0 10px 0; color: {status_color};">
                    {status_icon} {ep_name}
                </h4>
                <p style="margin: 0; font-size: 0.9em; color: #888;">
                    ⏱️ {elapsed_time}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if result_data["success"]:
                # 显示成功的转写结果
                with st.container():
                    # 直接显示完整内容，不再使用折叠块
                    st.markdown(result_data["result"])
                    
                    # 添加打开按钮
                    # 找到该端点对应的已保存文件
                    saved_file_path = None
                    for saved_ep, saved_path in saved_files:
                        if saved_ep == ep_name:
                            saved_file_path = saved_path
                            break
                    
                    if saved_file_path:
                        if st.button(f"📂 打开文件", key=f"{key_prefix}_open_{ep_name}_{idx}", use_container_width=True):
                            # 用系统默认应用打开已保存的文件
                            try:
                                subprocess.Popen(["open", saved_file_path])
                                st.success(f"✅ 已打开文件！")
                            except Exception as e:
                                st.error(f"无法打开文件: {e}")
            else:
                # 显示错误信息
                st.error(f"**错误:**\n{result_data['result']}")


# 检查是否有并发结果或历史记录
history_list = load_concurrent_history_list()
has_current_results = "current_concurrent_results" in st.session_state
has_history = len(history_list) > 0

# 如果有当前结果或历史记录，显示对比区
if has_current_results or has_history:
    st.markdown("---")
    st.markdown("## 并发结果对比区")
    
    # 决定默认显示哪个Tab（如果刚执行完并发转写，显示当前结果；否则显示历史）
    if has_current_results and st.session_state.get("show_concurrent_compare", False):
        # 刚执行完并发转写，默认显示当前结果
        default_tab_index = 0
        # 清除标记，避免下次刷新时还默认显示当前结果
        if "show_concurrent_compare" in st.session_state:
            del st.session_state["show_concurrent_compare"]
    else:
        # 否则默认显示历史对比
        default_tab_index = 1 if has_history and not has_current_results else 0
    
    # 创建标签页
    tab1, tab2 = st.tabs(["🎯 当前结果", "📚 历史对比"])
    
    with tab1:
        # 显示当前并发结果
        if "current_concurrent_results" in st.session_state:
            current_data = st.session_state["current_concurrent_results"]
            
            # 显示信息
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.info(f"**频道:** {current_data['channel']}")
            with col_info2:
                st.info(f"**时间:** {current_data['timestamp']}")
            with col_info3:
                stats = current_data['statistics']
                st.info(f"**结果:** {stats['success']}/{stats['total']} 成功")
            
            st.markdown("---")
            
            # 渲染结果
            render_concurrent_results(current_data, key_prefix="current")
        else:
            st.info("暂无当前并发结果，请先执行并发转写")
    
    with tab2:
        # 显示历史对比
        st.markdown("### 选择历史记录")
        
        # 使用已加载的历史列表（避免重复加载）
        if history_list:
            # 创建下拉选择框
            history_options = ["请选择历史记录..."] + [item[0] for item in history_list]
            selected_history = st.selectbox(
                "历史并发结果",
                history_options,
                key="history_selector"
            )
            
            if selected_history and selected_history != "请选择历史记录...":
                # 找到对应的历史记录
                selected_idx = history_options.index(selected_history) - 1
                history_file_path = history_list[selected_idx][1]
                history_metadata = history_list[selected_idx][2]
                
                # 显示历史信息
                col_h1, col_h2, col_h3 = st.columns(3)
                with col_h1:
                    st.info(f"**频道:** {history_metadata['channel']}")
                with col_h2:
                    st.info(f"**时间:** {history_metadata['timestamp']}")
                with col_h3:
                    stats = history_metadata['statistics']
                    st.info(f"**结果:** {stats['success']}/{stats['total']} 成功")
                
                st.markdown("---")
                
                # 从历史元数据重建结果数据结构
                history_results = {}
                history_saved_files = []
                
                for result_info in history_metadata['results']:
                    ep_name = result_info['endpoint']
                    
                    if result_info['success']:
                        # 成功的结果 - 从文件读取内容
                        file_path = result_info.get('file_path')
                        if file_path and os.path.exists(file_path):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                history_results[ep_name] = {
                                    "success": True,
                                    "result": content,
                                    "elapsed": result_info['elapsed']
                                }
                                history_saved_files.append((ep_name, file_path))
                            except Exception as e:
                                history_results[ep_name] = {
                                    "success": False,
                                    "result": f"无法读取文件: {e}",
                                    "elapsed": result_info['elapsed']
                                }
                        else:
                            history_results[ep_name] = {
                                "success": False,
                                "result": "文件不存在或已被删除",
                                "elapsed": result_info['elapsed']
                            }
                    else:
                        # 失败的结果
                        history_results[ep_name] = {
                            "success": False,
                            "result": result_info.get('error', '未知错误'),
                            "elapsed": result_info['elapsed']
                        }
                
                # 渲染历史结果
                history_data = {
                    "results": history_results,
                    "saved_files": history_saved_files
                }
                render_concurrent_results(history_data, key_prefix=f"history_{selected_idx}")
        else:
            st.info("暂无历史记录，执行并发转写后会自动保存")

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
        # 添加默认选项，避免自动加载第一个文件
        file_options = ["--- 请选择Markdown文件 ---"] + md_files
        
        # 如果 session_state 中有指定的文件，自动选中（来自转写操作）
        default_index = 0
        if "current_md_file" in st.session_state and st.session_state["current_md_file"] in md_files:
            # 只在首次触发时自动选中，用户手动选择后清除
            if st.session_state.get("auto_select_triggered", False):
                default_index = md_files.index(st.session_state["current_md_file"]) + 1
        
        selected = st.selectbox("选择Markdown文件：", file_options, index=default_index)
        
        # 如果用户手动选择了文件（非默认选项），清除自动选择标记
        if selected != "--- 请选择Markdown文件 ---":
            if "auto_select_triggered" in st.session_state:
                # 如果当前选择的不是自动触发的文件，清除标记
                if selected != st.session_state.get("current_md_file"):
                    del st.session_state["auto_select_triggered"]
                    if "current_md_file" in st.session_state:
                        del st.session_state["current_md_file"]
        
        # 只有用户选择了具体文件才加载
        if selected and selected != "--- 请选择Markdown文件 ---":
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
            # 显示提示信息
            st.info("👆 请从上方下拉框选择一个Markdown文件进行审核和预览")
            edited = ""
    else:
        st.info("暂无Markdown文件")

# 右侧：选择模板、HTML预览
with col2:
    if not md_files:
        st.info("请先在左侧选择Markdown文件")
    elif not selected or selected == "--- 请选择Markdown文件 ---":
        st.info("👈 请先在左侧选择Markdown文件")
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