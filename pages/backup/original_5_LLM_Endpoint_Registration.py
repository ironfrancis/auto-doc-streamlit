import sys
import os
import json
import streamlit as st
import requests

# 添加正确的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from language_manager import init_language, get_text, get_language
from path_manager import get_json_data_dir

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


st.set_page_config(page_title="LLM端点管理", layout="wide")

# 创建标签页
tab1, tab2 = st.tabs(["🔧 端点管理", "🧪 端点测试"])

# 第一个标签页：端点管理
with tab1:
    st.title("LLM端点管理")

# 使用与1_Creation_and_AI_Transcription.py相同的路径逻辑
from pathlib import Path
ENDPOINTS_PATH = Path(__file__).parent.parent / "config" / "llm_endpoints.json"
API_TYPES = ["OpenAI", "Magic", "Qwen", "Claude", "Other"]

# 读取已注册端点
def load_endpoints():
    if os.path.exists(ENDPOINTS_PATH):
        try:
            with open(ENDPOINTS_PATH, "r", encoding="utf-8") as f:
                endpoints = json.load(f)
                return endpoints
        except json.JSONDecodeError as e:
            st.error(f"❌ 端点配置文件格式错误: {e}")
            return []
        except Exception as e:
            st.error(f"❌ 加载端点配置失败: {e}")
            return []
    else:
        st.error(f"❌ 端点配置文件不存在: {ENDPOINTS_PATH}")
        return []

def save_endpoints(endpoints):
    with open(ENDPOINTS_PATH, "w", encoding="utf-8") as f:
        json.dump(endpoints, f, ensure_ascii=False, indent=2)

endpoints = load_endpoints()

st.subheader(get_text("registered"))

cols_per_row = 2
num_cards = len(endpoints) + 1
rows = (num_cards + cols_per_row - 1) // cols_per_row

if "edit_idx_ep" not in st.session_state:
    st.session_state["edit_idx_ep"] = None
if "show_key" not in st.session_state:
    st.session_state["show_key"] = {}
if "default_idx" not in st.session_state:
    st.session_state["default_idx"] = next((i for i, ep in enumerate(endpoints) if ep.get("default")), None)
if "test_result" not in st.session_state:
    st.session_state["test_result"] = {}

def test_endpoint(api_url, api_key, model, is_openai, api_type):
    import requests
    try:
        test_message = "你好呀，你是什么模型？"
        if is_openai:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {"model": model, "messages": [{"role": "user", "content": test_message}], "temperature": 0.1}
            resp = requests.post(api_url, headers=headers, json=data, timeout=180)
            meta = {"status_code": resp.status_code, "headers": dict(resp.headers)}
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    # 兼容data.messages[0].message.content结构
                    if "data" in result and "messages" in result["data"] and result["data"]["messages"]:
                        reply = result["data"]["messages"][0]["message"]["content"]
                    else:
                        reply = result["choices"][0]["message"]["content"]
                except Exception:
                    reply = resp.text
                return True, meta, reply
            else:
                return False, meta, resp.text
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
            resp = requests.post(api_url, headers=headers, json=data, timeout=180)
            meta = {"status_code": resp.status_code, "headers": dict(resp.headers)}
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    # 兼容data.messages[0].message.content结构
                    if "data" in result and "messages" in result["data"] and result["data"]["messages"]:
                        reply = result["data"]["messages"][0]["message"]["content"]
                    else:
                        reply = result["choices"][0]["message"]["content"]
                except Exception:
                    reply = resp.text
                return True, meta, reply
            else:
                return False, meta, resp.text
        else:
            return False, {"error": "不支持的API类型"}, ""
    except Exception as e:
        return False, {"error": str(e)}, ""

for row in range(rows):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        card_idx = row * cols_per_row + col_idx
        if card_idx < len(endpoints):
            ep = endpoints[card_idx]
            with cols[col_idx]:
                with st.expander(ep['name'], expanded=False):
                    # 只保留内容本身，去掉多余div
                    st.markdown(f"<b>{T['zh']['name']}:</b> {ep['name']}", unsafe_allow_html=True)
                    st.markdown(f"<b>{T['zh']['api_type']}:</b> {ep['api_type']}", unsafe_allow_html=True)
                    st.markdown(f"<b>{T['zh']['is_openai']}:</b> {'✅' if ep.get('is_openai_compatible') else '❌'}", unsafe_allow_html=True)
                    st.markdown(f"<b>{T['zh']['api_url']}:</b> {ep['api_url']}", unsafe_allow_html=True)
                    # API Key遮掩
                    key_shown = st.session_state["show_key"].get(card_idx, False)
                    key_val = ep['api_key'] if key_shown else ("*" * 8 if ep['api_key'] else "")
                    st.text_input(get_text("api_key"), value=key_val, type="default", disabled=True, key=f"showkey_{card_idx}")
                    if st.button(get_text("show") if not key_shown else get_text("hide"), key=f"showbtn_{card_idx}"):
                        st.session_state["show_key"][card_idx] = not key_shown
                        st.rerun()
                    st.markdown(f"<b>{T['zh']['model']}:</b> {ep['model']}", unsafe_allow_html=True)
                    st.markdown(f"<b>{T['zh']['temperature']}:</b> {ep.get('temperature', '')}", unsafe_allow_html=True)
                    st.markdown(f"<b>{T['zh']['remark']}:</b> {ep.get('remark', '')}", unsafe_allow_html=True)
                    if st.session_state["default_idx"] == card_idx:
                        st.markdown(f"<span style='color:green;font-weight:bold'>{T['zh']['default']}</span>", unsafe_allow_html=True)
                    btn_cols = st.columns(4)
                    with btn_cols[0]:
                        if st.button(get_text("edit"), key=f"edit_ep_{card_idx}"):
                            st.session_state["edit_idx_ep"] = card_idx
                            st.rerun()
                    with btn_cols[1]:
                        if st.button(get_text("delete"), key=f"del_ep_{card_idx}"):
                            endpoints.pop(card_idx)
                            save_endpoints(endpoints)
                            st.success(get_text("delete_success"))
                            st.rerun()
                    with btn_cols[2]:
                        if st.button(get_text("default"), key=f"setdef_ep_{card_idx}"):
                            for i, ep2 in enumerate(endpoints):
                                ep2["default"] = (i == card_idx)
                            save_endpoints(endpoints)
                            st.session_state["default_idx"] = card_idx
                            st.rerun()
                    # Test Endpoint单独一排，宽度与卡片一致
                    with st.container():
                        if st.button(get_text("test"), key=f"test_ep_{card_idx}"):
                            ok, meta, reply = test_endpoint(ep['api_url'], ep['api_key'], ep['model'], ep.get('is_openai_compatible', False), ep.get('api_type', ''))
                            st.session_state["test_result"] = {"idx": card_idx, "ok": ok, "meta": meta, "reply": reply}
                        if st.session_state.get("test_result", {}).get("idx") == card_idx:
                            with st.expander("测试结果", expanded=True):
                                st.code(f"元数据：\n{st.session_state['test_result']['meta']}", language="json")
                                st.code(f"模型回复：\n{st.session_state['test_result']['reply'] or '无回复'}", language="markdown")
                    if st.session_state["edit_idx_ep"] == card_idx:
                        # 编辑模式
                        new_name = st.text_input(get_text("name"), value=ep["name"], key=f"edit_ep_name_{card_idx}")
                        new_api_type = st.selectbox(get_text("api_type"), API_TYPES, index=API_TYPES.index(ep["api_type"]) if ep["api_type"] in API_TYPES else 0, key=f"edit_ep_type_{card_idx}")
                        new_is_openai = st.checkbox(get_text("is_openai"), value=ep.get("is_openai_compatible", False), key=f"edit_ep_isopenai_{card_idx}")
                        new_api_url = st.text_input(get_text("api_url"), value=ep["api_url"], key=f"edit_ep_url_{card_idx}")
                        new_api_key = st.text_input(get_text("api_key"), value=ep["api_key"], type="password", key=f"edit_ep_key_{card_idx}")
                        new_model = st.text_input(get_text("model"), value=ep["model"], key=f"edit_ep_model_{card_idx}")
                        new_temp = st.text_input(get_text("temperature"), value=str(ep.get("temperature", "")), key=f"edit_ep_temp_{card_idx}")
                        new_remark = st.text_area(get_text("remark"), value=ep.get("remark", ""), key=f"edit_ep_remark_{card_idx}")
                        save_col, cancel_col = st.columns(2)
                        with save_col:
                            if st.button(get_text("save"), key=f"save_ep_{card_idx}"):
                                endpoints[card_idx] = {
                                    "name": new_name,
                                    "api_type": new_api_type,
                                    "is_openai_compatible": new_is_openai,
                                    "api_url": new_api_url,
                                    "api_key": new_api_key,
                                    "model": new_model,
                                    "temperature": float(new_temp) if new_temp else None,
                                    "remark": new_remark,
                                    "default": (st.session_state["default_idx"] == card_idx)
                                }
                                save_endpoints(endpoints)
                                st.session_state["edit_idx_ep"] = None
                                st.success(get_text("edit_success"))
                                st.rerun()
                        with cancel_col:
                            if st.button(get_text("cancel"), key=f"cancel_ep_{card_idx}"):
                                st.session_state["edit_idx_ep"] = None
                                st.rerun()
        elif card_idx == len(endpoints):
            # 新建端点卡片
            with cols[col_idx]:
                with st.expander(get_text("new_endpoint"), expanded=False):
                    # 只保留内容本身，去掉多余div
                    st.markdown(f"<b>{T['zh']['new_endpoint']}</b>", unsafe_allow_html=True)
                    name = st.text_input(get_text("name"), key=f"reg_ep_name_{card_idx}")
                    api_type = st.selectbox(get_text("api_type"), API_TYPES, key=f"reg_ep_type_{card_idx}")
                    is_openai = st.checkbox(get_text("is_openai"), value=(api_type=="OpenAI"), key=f"reg_ep_isopenai_{card_idx}")
                    api_url = st.text_input(get_text("api_url"), key=f"reg_ep_url_{card_idx}")
                    api_key = st.text_input(get_text("api_key"), type="password", key=f"reg_ep_key_{card_idx}")
                    model = st.text_input(get_text("model"), key=f"reg_ep_model_{card_idx}")
                    temp = st.text_input(get_text("temperature"), key=f"reg_ep_temp_{card_idx}")
                    remark = st.text_area(get_text("remark"), key=f"reg_ep_remark_{card_idx}")
                    set_default = st.checkbox(get_text("default"), key=f"reg_ep_default_{card_idx}")
                    if st.button(get_text("submit"), key=f"reg_ep_submit_{card_idx}"):
                        if not name.strip():
                            st.warning("Please input endpoint name!" if get_text("get_language()")=="en" else "请输入端点名称！")
                        else:
                            if set_default:
                                for ep in endpoints:
                                    ep["default"] = False
                            endpoint = {
                                "name": name,
                                "api_type": api_type,
                                "is_openai_compatible": is_openai,
                                "api_url": api_url,
                                "api_key": api_key,
                                "model": model,
                                "temperature": float(temp) if temp else None,
                                "remark": remark,
                                "default": set_default
                            }
                            endpoints.append(endpoint)
                            save_endpoints(endpoints)
                            st.success(get_text("success"))
                            st.rerun() 

# 第二个标签页：端点测试
with tab2:
    st.title("LLM Endpoint & Prompt 测试工具")
    
    # 读取端点
    if os.path.exists(ENDPOINTS_PATH):
        try:
            with open(ENDPOINTS_PATH, "r", encoding="utf-8") as f:
                test_endpoints = json.load(f)
        except Exception as e:
            st.error(f"加载端点配置失败: {e}")
            test_endpoints = []
    else:
        st.error(f"端点配置文件不存在: {ENDPOINTS_PATH}")
        test_endpoints = []
    test_endpoint_names = [ep["name"] for ep in test_endpoints] if test_endpoints else []
    
    col1, col2 = st.columns(2)
    with col1:
        selected_endpoint = st.selectbox("选择LLM端点", test_endpoint_names) if test_endpoint_names else ""
        prompt = st.text_area("提示词 (Prompt)", height=120)
        if st.button("测试LLM回复"):
            if not selected_endpoint or not prompt.strip():
                st.warning("请选择端点并输入提示词！")
            else:
                ep = next((e for e in test_endpoints if e["name"] == selected_endpoint), None)
                if not ep:
                    st.error("端点未找到！")
                else:
                    # 构造请求
                    api_type = ep.get("api_type", "")
                    api_url = ep.get("api_url", "")
                    api_key = ep.get("api_key", "")
                    model = ep.get("model", "")
                    is_openai = ep.get("is_openai_compatible", False)
                    try:
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
                            st.error("暂不支持该API类型")
                            resp = None
                        if resp is not None:
                            meta = {"status_code": resp.status_code, "headers": dict(resp.headers)}
                            if resp.status_code == 200:
                                try:
                                    result = resp.json()
                                    if "data" in result and "messages" in result["data"] and result["data"]["messages"]:
                                        reply = result["data"]["messages"][0]["message"]["content"]
                                    else:
                                        reply = result["choices"][0]["message"]["content"]
                                except Exception:
                                    reply = resp.text
                                st.success("测试成功！")
                                st.code(f"元数据：\n{meta}", language="json")
                                st.code(f"模型回复：\n{reply or '无回复'}", language="markdown")
                            else:
                                st.error(f"测试失败，状态码：{resp.status_code}")
                                st.code(f"响应内容：\n{resp.text}")
                    except Exception as e:
                        st.error(f"请求异常：{e}")
    
    with col2:
        st.info("本页面用于快速测试不同端点和提示词组合，适合调试和对比LLM效果。\n\n左侧选择端点并输入提示词，点击测试即可实时查看回复。")
        st.info("⏱️ **注意：** 测试超时时间已设置为180秒，适合处理需要较长推理时间的模型。")