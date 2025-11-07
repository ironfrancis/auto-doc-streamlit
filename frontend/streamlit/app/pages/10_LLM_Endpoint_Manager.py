#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 端点管理页面 - 完全使用 API，不依赖文件
现代化的UI设计，提供更好的用户体验
"""

import streamlit as st
import requests
from core.utils.language_manager import init_language, get_text, get_language
from core.utils.theme_loader import load_anthropic_theme
from core.utils.icon_library import get_icon
from core.utils.api_client import APIClient, APIError, APIConnectionError

# 简洁的CSS样式
st.markdown("""
<style>
/* 简洁的卡片样式 */
.endpoint-card {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    background-color: #ffffff;
}

.endpoint-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.endpoint-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0;
}

.endpoint-badge {
    background-color: #f3f4f6;
    color: #6b7280;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
}

.endpoint-info {
    color: #6b7280;
    font-size: 0.875rem;
    line-height: 1.4;
}

.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 0.5rem;
}

.status-online { background-color: #10b981; }
.status-offline { background-color: #ef4444; }

/* 表单容器 */
.form-container {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
    background-color: #f9fafb;
    margin-bottom: 1rem;
}

/* 空状态 */
.empty-state {
    text-align: center;
    padding: 2rem 1rem;
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)

# 多语言文本定义
T = {
    "zh": {
        "page_title": "LLM端点注册",
        "name": "端点名称",
        "api_type": "API类型",
        "is_openai": "OpenAI兼容",
        "api_url": "API地址",
        "api_key": "API密钥",
        "model": "模型名称",
        "temperature": "温度",
        "remark": "备注",
        "default": "默认端点",
        "new_endpoint": "新端点",
        "submit": "提交"
    },
    "en": {
        "page_title": "LLM Endpoint Registration",
        "name": "Endpoint Name",
        "api_type": "API Type",
        "is_openai": "OpenAI Compatible",
        "api_url": "API URL",
        "api_key": "API Key",
        "model": "Model Name",
        "temperature": "Temperature",
        "remark": "Remark",
        "default": "Default Endpoint",
        "new_endpoint": "New Endpoint",
        "submit": "Submit"
    }
}

# 初始化语言设置
init_language()

st.set_page_config(page_title="LLM端点管理", layout="wide")

# 加载主题
load_anthropic_theme()

# 创建标签页
tab1, tab2 = st.tabs(["端点管理", "端点测试"])

# 第一个标签页：端点管理
with tab1:
    st.markdown("## LLM 端点管理")

API_TYPES = ["OpenAI", "Magic", "Qwen", "Claude", "Other"]

# 初始化 API 客户端
try:
    api_client = APIClient()
    api_available = True
except Exception as e:
    st.error(f"无法连接到 API 服务器: {str(e)}")
    api_available = False
    api_client = None

# 读取已注册端点（完全使用 API，不回退到文件）
@st.cache_data(ttl=10)
def load_endpoints():
    """从 API 加载端点列表"""
    if not api_available:
        return []
    try:
        endpoints_data = api_client.get_llm_endpoints()
        # 转换 API 格式到页面期望的格式
        converted_endpoints = []
        for ep in endpoints_data:
            converted_ep = api_client.convert_llm_endpoint_to_legacy_format(ep)
            converted_endpoints.append(converted_ep)
        return converted_endpoints
    except (APIError, APIConnectionError) as e:
        st.error(f"获取端点失败: {str(e)}")
        return []
    except Exception as e:
        st.error(f"获取端点失败: {str(e)}")
        return []

def create_endpoint(endpoint_data: dict) -> bool:
    """创建新端点"""
    if not api_available:
        st.error("API 不可用，无法创建端点")
        return False
    try:
        api_endpoint = api_client.convert_llm_endpoint_to_api_format(endpoint_data)
        api_client.create_llm_endpoint(api_endpoint)
        # 清除缓存，但不立即刷新，让调用者决定何时刷新
        load_endpoints.clear()
        return True
    except APIError as e:
        st.error(f"创建端点失败: {str(e)}")
        return False
    except Exception as e:
        st.error(f"创建端点失败: {str(e)}")
        return False

def update_endpoint(endpoint_id: str, endpoint_data: dict) -> bool:
    """更新端点"""
    if not api_available:
        st.error("API 不可用，无法更新端点")
        return False
    try:
        api_endpoint = api_client.convert_llm_endpoint_to_api_format(endpoint_data)
        api_client.update_llm_endpoint(endpoint_id, api_endpoint)
        # 清除缓存，但不立即刷新，让调用者决定何时刷新
        load_endpoints.clear()
        return True
    except APIError as e:
        st.error(f"更新端点失败: {str(e)}")
        return False
    except Exception as e:
        st.error(f"更新端点失败: {str(e)}")
        return False

def delete_endpoint(endpoint_id: str) -> bool:
    """删除端点"""
    if not api_available:
        st.error("API 不可用，无法删除端点")
        return False
    try:
        api_client.delete_llm_endpoint(endpoint_id)
        # 清除缓存，但不立即刷新，让调用者决定何时刷新
        load_endpoints.clear()
        return True
    except APIError as e:
        st.error(f"删除端点失败: {str(e)}")
        return False
    except Exception as e:
        st.error(f"删除端点失败: {str(e)}")
        return False

def set_default_endpoint(endpoint_id: str) -> bool:
    """设置默认端点"""
    if not api_available:
        st.error("API 不可用，无法设置默认端点")
        return False
    try:
        # 获取当前端点信息
        endpoint = api_client.get_llm_endpoint(endpoint_id)
        if not endpoint:
            st.error("端点不存在")
            return False
        
        # 转换为页面格式，设置默认标志
        legacy_endpoint = api_client.convert_llm_endpoint_to_legacy_format(endpoint)
        legacy_endpoint["default"] = True
        
        # 转换回 API 格式并更新
        api_endpoint_data = api_client.convert_llm_endpoint_to_api_format(legacy_endpoint)
        api_client.update_llm_endpoint(endpoint_id, api_endpoint_data)
        # 清除缓存，但不立即刷新，让调用者决定何时刷新
        load_endpoints.clear()
        return True
    except APIError as e:
        st.error(f"设置默认端点失败: {str(e)}")
        return False
    except Exception as e:
        st.error(f"设置默认端点失败: {str(e)}")
        return False

# 检查 API 可用性
if not api_available:
    st.error("⚠️ API 服务器不可用，请检查 API 配置和连接")
    st.stop()

# 加载端点列表
endpoints = load_endpoints()

# 初始化 session state
if "edit_idx_ep" not in st.session_state:
    st.session_state["edit_idx_ep"] = None
if "show_key" not in st.session_state:
    st.session_state["show_key"] = {}
if "test_result" not in st.session_state:
    st.session_state["test_result"] = {}
if "show_new_form" not in st.session_state:
    st.session_state["show_new_form"] = False

# 找到默认端点的索引
default_idx = next((i for i, ep in enumerate(endpoints) if ep.get("default")), None)

def test_endpoint(api_url, api_key, model, is_openai, api_type):
    """测试端点连接"""
    try:
        test_message = "你好，请简单介绍一下你自己。"
        if is_openai:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {"model": model, "messages": [{"role": "user", "content": test_message}], "temperature": 0.1}
            resp = requests.post(api_url, headers=headers, json=data, timeout=30)  # 缩短超时时间
            meta = {"status_code": resp.status_code, "headers": dict(resp.headers)}
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    # 兼容data.messages[0].message.content结构
                    if "data" in result and "messages" in result["data"] and result["data"]["messages"]:
                        reply = result["data"]["messages"][0]["message"]["content"]
                    else:
                        reply = result["choices"][0]["message"]["content"]
                except Exception as json_error:
                    reply = resp.text[:500]  # 限制回复长度
                return True, meta, reply
            else:
                error_msg = resp.text[:500] if resp.text else f"HTTP {resp.status_code}"
                return False, meta, error_msg
        elif api_type == "Magic":
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "你是一个有帮助的助手。"},
                    {"role": "user", "content": test_message}
                ],
                "temperature": 0.1,
                "stream": False
            }
            resp = requests.post(api_url, headers=headers, json=data, timeout=30)  # 缩短超时时间
            meta = {"status_code": resp.status_code, "headers": dict(resp.headers)}
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    # 兼容data.messages[0].message.content结构
                    if "data" in result and "messages" in result["data"] and result["data"]["messages"]:
                        reply = result["data"]["messages"][0]["message"]["content"]
                    else:
                        reply = result["choices"][0]["message"]["content"]
                except Exception as json_error:
                    reply = resp.text[:500]  # 限制回复长度
                return True, meta, reply
            else:
                error_msg = resp.text[:500] if resp.text else f"HTTP {resp.status_code}"
                return False, meta, error_msg
        else:
            return False, {"error": f"不支持的API类型: {api_type}"}, ""
    except requests.exceptions.Timeout as e:
        return False, {"error": f"请求超时 (30秒): {str(e)}"}, ""
    except requests.exceptions.ConnectionError as e:
        return False, {"error": f"连接失败: {str(e)}"}, ""
    except requests.exceptions.HTTPError as e:
        return False, {"error": f"HTTP错误: {str(e)}"}, ""
    except requests.exceptions.RequestException as e:
        return False, {"error": f"请求异常: {type(e).__name__} - {str(e)}"}, ""
    except Exception as e:
        return False, {"error": f"未知错误: {type(e).__name__} - {str(e)}"}, ""

# 顶部操作栏
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("新建端点", type="primary", use_container_width=True):
        st.session_state["show_new_form"] = not st.session_state.get("show_new_form", False)
        st.session_state["edit_idx_ep"] = None
        st.rerun()

with col2:
    if endpoints:
        st.info(f"共 {len(endpoints)} 个端点")
    else:
        st.info("暂无端点")

# 显示端点列表
if endpoints:
    for idx, ep in enumerate(endpoints):
        ep_id = ep.get("id", "")
        is_editing = st.session_state.get("edit_idx_ep") == idx
        is_default = default_idx == idx

        if is_editing:
            # 编辑模式
            with st.expander(f"编辑端点: {ep['name']}", expanded=True):
                with st.form(key=f"edit_form_{idx}", clear_on_submit=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("端点名称", value=ep["name"], key=f"name_{idx}")
                        new_api_type = st.selectbox("API类型", API_TYPES,
                            index=API_TYPES.index(ep["api_type"]) if ep["api_type"] in API_TYPES else 0,
                            key=f"type_{idx}")
                        new_api_url = st.text_input("API地址", value=ep["api_url"], key=f"url_{idx}")
                        new_api_key = st.text_input("API密钥", value=ep["api_key"], type="password", key=f"key_{idx}")

                    with col2:
                        new_model = st.text_input("模型名称", value=ep["model"], key=f"model_{idx}")
                        new_temp = st.number_input("温度", value=float(ep.get("temperature", 0.7)), min_value=0.0, max_value=2.0, step=0.1, key=f"temp_{idx}")
                        new_is_openai = st.checkbox("OpenAI兼容", value=ep.get("is_openai_compatible", False), key=f"openai_{idx}")
                        new_remark = st.text_input("备注", value=ep.get("remark", ""), key=f"remark_{idx}")

                    col_save, col_cancel = st.columns([1, 1])
                    with col_save:
                        if st.form_submit_button("保存", type="primary", use_container_width=True):
                            if new_name.strip():
                                endpoint_data = {
                                    "name": new_name, "api_type": new_api_type, "is_openai_compatible": new_is_openai,
                                    "api_url": new_api_url, "api_key": new_api_key, "model": new_model,
                                    "temperature": new_temp, "remark": new_remark, "default": is_default
                                }
                                if update_endpoint(ep_id, endpoint_data):
                                    st.session_state["edit_idx_ep"] = None
                                    st.rerun()
                    with col_cancel:
                        if st.form_submit_button("取消", use_container_width=True):
                            st.session_state["edit_idx_ep"] = None
                            st.rerun()
        else:
            # 查看模式 - 简洁列表
            with st.container():
                col_name, col_actions = st.columns([3, 1])

                with col_name:
                    name_text = ep['name']
                    if is_default:
                        name_text += " ⭐"
                    st.subheader(name_text)

                    info_text = f"{ep['api_type']} • {ep.get('model', 'N/A')} • 温度: {ep.get('temperature', 'N/A')}"
                    if ep.get('remark'):
                        info_text += f" • {ep['remark']}"
                    st.caption(info_text)

                    # 显示测试结果
                    if st.session_state.get("test_result", {}).get("idx") == idx:
                        result = st.session_state["test_result"]
                        if result.get("ok"):
                            reply_preview = result.get('reply', '')[:100] + "..." if len(result.get('reply', '')) > 100 else result.get('reply', '')
                            st.success("✅ 测试成功")
                            st.caption(f"响应预览: {reply_preview}")
                        else:
                            st.error("❌ 测试失败")
                            error_info = result.get('meta', {}).get('error', '未知错误')
                            st.caption(f"错误: {error_info}")
                            if st.button("查看详情", key=f"error_detail_{idx}"):
                                with st.expander("错误详情", expanded=True):
                                    st.json(result.get('meta', {}))

                with col_actions:
                    st.markdown("**操作**")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        if st.button("编辑", key=f"edit_{idx}", use_container_width=True):
                            st.session_state["edit_idx_ep"] = idx
                            st.session_state["show_new_form"] = False
                            st.rerun()

                    with col2:
                        if st.button("测试", key=f"test_{idx}", use_container_width=True):
                            with st.spinner("测试中..."):
                                ok, meta, reply = test_endpoint(
                                    ep['api_url'], ep['api_key'], ep['model'],
                                    ep.get('is_openai_compatible', False), ep.get('api_type', '')
                                )
                                st.session_state["test_result"] = {"idx": idx, "ok": ok, "meta": meta, "reply": reply}
                                st.rerun()

                    with col3:
                        if st.button("默认", key=f"def_{idx}", use_container_width=True, disabled=is_default):
                            if set_default_endpoint(ep_id):
                                st.rerun()

                    with col4:
                        if st.button("删除", key=f"del_{idx}", use_container_width=True):
                            if delete_endpoint(ep_id):
                                st.rerun()

                st.divider()
else:
    st.info("暂无端点，点击上方按钮创建")

# 新建端点表单
if st.session_state.get("show_new_form"):
    with st.expander("新建端点", expanded=True):
        with st.form(key="new_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                new_name = st.text_input("端点名称", key="new_name")
                new_api_type = st.selectbox("API类型", API_TYPES, key="new_type")
                new_api_url = st.text_input("API地址", key="new_url")
                new_api_key = st.text_input("API密钥", type="password", key="new_key")

            with col2:
                new_model = st.text_input("模型名称", key="new_model")
                new_temp = st.number_input("温度", value=0.7, min_value=0.0, max_value=2.0, step=0.1, key="new_temp")
                new_is_openai = st.checkbox("OpenAI兼容", value=False, key="new_openai")
                new_remark = st.text_input("备注", key="new_remark")

            new_set_default = st.checkbox("设为默认端点", key="new_default")

            col_create, col_cancel = st.columns([1, 1])
            with col_create:
                if st.form_submit_button("创建", type="primary", use_container_width=True):
                    if new_name.strip():
                        endpoint_data = {
                            "name": new_name, "api_type": new_api_type, "is_openai_compatible": new_is_openai,
                            "api_url": new_api_url, "api_key": new_api_key, "model": new_model,
                            "temperature": new_temp, "remark": new_remark, "default": new_set_default
                        }
                        if create_endpoint(endpoint_data):
                            st.session_state["show_new_form"] = False
                            st.rerun()
                    else:
                        st.error("端点名称不能为空")
            with col_cancel:
                if st.form_submit_button("取消", use_container_width=True):
                    st.session_state["show_new_form"] = False
                    st.rerun()

# 第二个标签页：端点测试
with tab2:
    st.markdown("## 端点测试")

    test_endpoints = load_endpoints()
    test_endpoint_names = [ep["name"] for ep in test_endpoints] if test_endpoints else []

    if test_endpoints:
        selected_endpoint = st.selectbox("选择端点", test_endpoint_names)
        prompt = st.text_area("测试提示词", height=100, placeholder="输入测试内容...")

        if st.button("测试", type="primary"):
            if selected_endpoint and prompt.strip():
                ep = next((e for e in test_endpoints if e["name"] == selected_endpoint), None)
                if ep:
                    api_type = ep.get("api_type", "")
                    api_url = ep.get("api_url", "")
                    api_key = ep.get("api_key", "")
                    model = ep.get("model", "")
                    is_openai = ep.get("is_openai_compatible", False)

                    try:
                        with st.spinner("测试中..."):
                            if is_openai:
                                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                                data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
                                resp = requests.post(api_url, headers=headers, json=data, timeout=180)
                            elif api_type == "Magic":
                                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                                data = {
                                    "model": model,
                                    "messages": [
                                        {"role": "system", "content": "你是一个有帮助的助手。"},
                                        {"role": "user", "content": prompt}
                                    ],
                                    "temperature": 0.7,
                                    "stream": False
                                }
                                resp = requests.post(api_url, headers=headers, json=data, timeout=180)
                            else:
                                st.error("不支持该API类型")
                                resp = None

                            if resp and resp.status_code == 200:
                                try:
                                    result = resp.json()
                                    if "data" in result and "messages" in result["data"] and result["data"]["messages"]:
                                        reply = result["data"]["messages"][0]["message"]["content"]
                                    else:
                                        reply = result["choices"][0]["message"]["content"]
                                except Exception:
                                    reply = resp.text

                                st.success("测试成功")
                                st.text_area("响应内容", reply, height=200, disabled=True)
                            elif resp:
                                st.error(f"测试失败 ({resp.status_code})")
                                with st.expander("查看错误详情"):
                                    st.code(resp.text[:1000])
                                    if resp.headers.get('content-type'):
                                        st.caption(f"Content-Type: {resp.headers['content-type']}")
                            else:
                                st.error("未收到响应")

                    except requests.exceptions.Timeout as e:
                        st.error("请求超时")
                        with st.expander("超时详情"):
                            st.code(f"超时时间: 180秒\n错误信息: {str(e)}")
                    except requests.exceptions.ConnectionError as e:
                        st.error("连接失败")
                        with st.expander("连接错误详情"):
                            st.code(f"API地址: {api_url}\n错误信息: {str(e)}")
                    except requests.exceptions.HTTPError as e:
                        st.error("HTTP错误")
                        with st.expander("HTTP错误详情"):
                            st.code(f"错误信息: {str(e)}")
                    except requests.exceptions.RequestException as e:
                        st.error("请求异常")
                        with st.expander("请求异常详情"):
                            st.code(f"异常类型: {type(e).__name__}\n错误信息: {str(e)}")
                    except Exception as e:
                        st.error(f"未知错误: {type(e).__name__}")
                        with st.expander("详细错误信息"):
                            st.code(f"异常类型: {type(e).__name__}\n错误信息: {str(e)}")

                            # 显示端点配置信息（隐藏敏感信息）
                            st.write("端点配置:")
                            config_info = {
                                "API类型": api_type,
                                "API地址": api_url,
                                "模型": model,
                                "OpenAI兼容": is_openai,
                                "API密钥": f"{api_key[:8]}..." if api_key and len(api_key) > 8 else "无"
                            }
                            for key, value in config_info.items():
                                st.code(f"{key}: {value}")
            else:
                st.error("请选择端点并输入测试内容")
    else:
        st.info("暂无可测试的端点，请先创建端点")
