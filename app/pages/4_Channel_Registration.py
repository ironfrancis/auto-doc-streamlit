import sys
import os
import json
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import streamlit as st

TEXTS = {
    "en": {
        "page_title": "Channel Registration",
        "name": "Channel Name",
        "desc": "Channel Style/Description",
        "default_prompt": "Default Prompt",
        "custom_prompt": "Custom Prompt (optional)",
        "template": "Select HTML Template",
        "submit": "Register Channel",
        "success": "Channel registered successfully!",
        "registered": "Registered Channels",
        "edit": "Edit",
        "save": "Save",
        "cancel": "Cancel",
        "edit_success": "Channel updated successfully!",
        "new_channel": "➕ New Channel",
        "lang": "Language",
    },
    "zh": {
        "page_title": "频道注册",
        "name": "频道名称",
        "desc": "频道风格/描述",
        "default_prompt": "默认提示词",
        "custom_prompt": "自定义提示词（可选）",
        "template": "选择HTML模板",
        "submit": "注册频道",
        "success": "频道注册成功！",
        "registered": "已注册频道",
        "edit": "修改",
        "save": "保存",
        "cancel": "取消",
        "edit_success": "频道修改成功！",
        "new_channel": "➕ 新建频道",
        "lang": "语言",
    }
}

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

with st.sidebar:
    lang = st.selectbox("语言 / Language", ["zh", "en"], index=0 if st.session_state.get("lang", "zh") == "zh" else 1, key="lang_global")
    if lang != st.session_state.get("lang", "zh"):
        st.session_state["lang"] = lang
T = TEXTS[lang]

st.set_page_config(page_title=T["page_title"], layout="wide")
st.title(T["page_title"])

TEMPLATE_DIR = "app/html_templates"
CHANNELS_PATH = "app/channels.json"
ENDPOINTS_PATH = "app/llm_endpoints.json"
# 读取端点
if os.path.exists(ENDPOINTS_PATH):
    with open(ENDPOINTS_PATH, "r", encoding="utf-8") as f:
        endpoints = json.load(f)
else:
    endpoints = []
endpoint_names = [ep["name"] for ep in endpoints] if endpoints else []

# 读取已注册频道
def load_channels():
    if os.path.exists(CHANNELS_PATH):
        with open(CHANNELS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_channels(channels):
    with open(CHANNELS_PATH, "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

channels = load_channels()

st.subheader(T["registered"])

# 卡片式布局，每行3个
cols_per_row = 3
num_cards = len(channels) + 1  # +1 for new channel
rows = (num_cards + cols_per_row - 1) // cols_per_row

if "edit_idx" not in st.session_state:
    st.session_state["edit_idx"] = None

for row in range(rows):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        card_idx = row * cols_per_row + col_idx
        if card_idx < len(channels):
            channel = channels[card_idx]
            with cols[col_idx]:
                with st.container():
                    st.markdown(f"<div style='border:1px solid #eee; border-radius:10px; padding:18px 14px 10px 14px; margin-bottom:10px; background:#fafbfc;'>", unsafe_allow_html=True)
                    st.markdown(f"<b>{T['name']}:</b> {channel['name']}", unsafe_allow_html=True)
                    st.markdown(f"<b>{T['desc']}:</b> {channel['description']}", unsafe_allow_html=True)
                    st.markdown(f"<b>{T['template']}:</b> {channel['template']}", unsafe_allow_html=True)
                    st.markdown(f"<b>LLM端点:</b> {channel.get('llm_endpoint', '')}", unsafe_allow_html=True)
                    if st.session_state["edit_idx"] == card_idx:
                        # 编辑模式
                        new_name = st.text_input(T["name"], value=channel["name"], key=f"edit_name_{card_idx}")
                        new_desc = st.text_area(T["desc"], value=channel["description"], height=40, key=f"edit_desc_{card_idx}")
                        template_files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.html')]
                        new_template = st.selectbox(T["template"], template_files, index=template_files.index(channel["template"]) if channel["template"] in template_files else 0, key=f"edit_template_{card_idx}")
                        new_llm_endpoint = st.selectbox("LLM端点", endpoint_names, index=endpoint_names.index(channel.get("llm_endpoint", endpoint_names[0])) if channel.get("llm_endpoint") in endpoint_names else 0, key=f"edit_llm_{card_idx}")
                        save_col, cancel_col = st.columns(2)
                        with save_col:
                            if st.button(T["save"], key=f"save_{card_idx}"):
                                channels[card_idx] = {
                                    "name": new_name,
                                    "description": new_desc,
                                    "template": new_template,
                                    "llm_endpoint": new_llm_endpoint
                                }
                                save_channels(channels)
                                st.session_state["edit_idx"] = None
                                st.success(T["edit_success"])
                                st.rerun()
                        with cancel_col:
                            if st.button(T["cancel"], key=f"cancel_{card_idx}"):
                                st.session_state["edit_idx"] = None
                                st.rerun()
                    else:
                        if st.button(T["edit"], key=f"edit_{card_idx}"):
                            st.session_state["edit_idx"] = card_idx
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        elif card_idx == len(channels):
            # 新建频道卡片
            with cols[col_idx]:
                with st.container():
                    st.markdown(f"<div style='border:2px dashed #bbb; border-radius:10px; padding:18px 14px 10px 14px; margin-bottom:10px; background:#f6f7fa;'>", unsafe_allow_html=True)
                    st.markdown(f"<b>{T['new_channel']}</b>", unsafe_allow_html=True)
                    name = st.text_input(T["name"], key=f"reg_name_{card_idx}")
                    desc = st.text_area(T["desc"], height=40, key=f"reg_desc_{card_idx}")
                    template_files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.html')]
                    template_choice = st.selectbox(T["template"], template_files, key=f"reg_template_{card_idx}")
                    reg_llm_endpoint = st.selectbox("LLM端点", endpoint_names, key=f"reg_llm_endpoint_{card_idx}")
                    if st.button(T["submit"], key=f"reg_submit_{card_idx}"):
                        if not name.strip():
                            st.warning("Please input channel name!" if lang=="en" else "请输入频道名称！")
                        else:
                            channel = {
                                "name": name,
                                "description": desc,
                                "template": template_choice,
                                "llm_endpoint": reg_llm_endpoint
                            }
                            channels.append(channel)
                            save_channels(channels)
                            st.success(T["success"])
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True) 