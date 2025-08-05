import sys
import os
import json
import datetime
import subprocess

# 添加正确的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import streamlit as st
from language_manager import init_language, get_text
from path_manager import get_static_dir, get_md_review_dir, get_json_data_dir
import requests

# 多语言文本定义
T = {
    "zh": {
        "page_title": "AI内容创作与转写",
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

HISTORY_PATH = get_json_data_dir() / "md_transcribe_history.json"

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

st.set_page_config(page_title=get_text("page_title"), layout="wide")
st.title(get_text("page_title"))

STATIC_DIR = get_static_dir()
CHANNELS_PATH = get_json_data_dir() / "channels.json"
ENDPOINTS_PATH = get_json_data_dir() / "llm_endpoints.json"
os.makedirs(STATIC_DIR, exist_ok=True)

# 读取频道
if os.path.exists(CHANNELS_PATH):
    with open(CHANNELS_PATH, "r", encoding="utf-8") as f:
        channels = json.load(f)
else:
    channels = []

channel_names = [c["name"] for c in channels] if channels else []
# 频道和端点选择同一行
sel_col1, sel_col2 = st.columns([1, 1])
with sel_col1:
    selected_channel = st.selectbox(get_text("select_channel"), ["-"] + channel_names)
with sel_col2:
    # 获取频道对象
    channel_obj = next((c for c in channels if c["name"] == selected_channel), None)
    # 读取LLM端点
    if os.path.exists(ENDPOINTS_PATH):
        with open(ENDPOINTS_PATH, "r", encoding="utf-8") as f:
            endpoints = json.load(f)
    else:
        endpoints = []
    endpoint_names = [ep["name"] for ep in endpoints] if endpoints else []
    # 联动：频道指定端点优先选中
    if channel_obj and channel_obj.get("llm_endpoint") in endpoint_names:
        endpoint_index = endpoint_names.index(channel_obj["llm_endpoint"])
    else:
        endpoint_index = 0
    selected_endpoint = st.selectbox("选择LLM端点", endpoint_names, index=endpoint_index) if endpoint_names else ""

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
        
        # 整合频道特定的prompt
        channel_prompt = channel_obj.get("description", "") if channel_obj else ""
        full_prompt = f"频道：{selected_channel}\n\n频道风格提示：\n{channel_prompt}\n\n输入内容：\n{input_content}"
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
                if is_openai:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    data = {"model": model, "messages": [{"role": "user", "content": full_prompt}], "temperature": temperature}
                    resp = requests.post(api_url, headers=headers, json=data, timeout=120)
                elif api_type == "Magic":
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    data = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "你是一个有帮助的助手。"},
                            {"role": "user", "content": full_prompt}
                        ],
                        "temperature": temperature,
                        "stream": False
                    }
                    resp = requests.post(api_url, headers=headers, json=data, timeout=120)
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
                        md_review_dir = "app/md_review"
                        os.makedirs(md_review_dir, exist_ok=True)
                        local_md_path = os.path.join(md_review_dir, f"{safe_channel}_{ts}.md")
                        with open(local_md_path, "w", encoding="utf-8") as f:
                            f.write(md_result)
                        # 用Typora打开
                        try:
                            subprocess.Popen(["open", "-a", "Typora", local_md_path])
                        except Exception as e:
                            st.info(f"无法自动打开Typora: {e}")
                        st.success(get_text("success"))
                    else:
                        st.error(f"AI转写失败: {resp.text}")
            except Exception as e:
                st.error(f"请求失败: {e}")

# Markdown Preview独占一行
st.markdown("---")
st.subheader(get_text("md_preview"))
ai_md = st.session_state.get("ai_md_result", "")
if ai_md:
    st.markdown(ai_md)
    md_url = "/static/preview.md"
    # 获取当前语言
    current_lang = get_language() if hasattr(get_language, '__call__') else "zh"
    link_text = T[current_lang]['md_newtab']
    st.markdown(f"[{link_text}](http://localhost:8501{md_url})", unsafe_allow_html=True) 