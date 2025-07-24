import sys
import os
import json
import datetime
import subprocess
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import streamlit as st
import requests

HISTORY_PATH = "app/md_transcribe_history.json"

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

TEXTS = {
    "en": {
        "page_title": "AI Content Creation & Transcription",
        "select_channel": "Select Channel",
        "input_type": "Input Type",
        "input_content": "Input Content (draft, Markdown, or link)",
        "channel": "Channel/Style (e.g. AGI Apocalypse)",
        "style": "Channel Style/Description",
        "default_prompt": "Default Prompt",
        "custom_prompt": "Custom Prompt (optional)",
        "template": "HTML Template",
        "transcribe_btn": "AI Transcribe",
        "success": "AI transcription succeeded! Preview on the right or in a new tab.",
        "md_preview": "Markdown Preview:",
        "md_newtab": "👉 Preview Markdown in New Tab",
        "lang": "Language",
    },
    "zh": {
        "page_title": "AI内容创作与转写",
        "select_channel": "选择频道",
        "input_type": "输入类型",
        "input_content": "输入内容（初稿、Markdown或链接）",
        "channel": "频道/风格（如AGI启示录）",
        "style": "频道风格/描述",
        "default_prompt": "默认提示词",
        "custom_prompt": "自定义提示词（可选）",
        "template": "HTML模板",
        "transcribe_btn": "AI转写",
        "success": "AI转写成功！请在右侧或新标签页预览。",
        "md_preview": "Markdown预览：",
        "md_newtab": "👉 新标签页预览Markdown",
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

STATIC_DIR = "app/static"
CHANNELS_PATH = "app/channels.json"
ENDPOINTS_PATH = "app/llm_endpoints.json"
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
    selected_channel = st.selectbox(T["select_channel"], ["-"] + channel_names)
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
if st.button(T["transcribe_btn"]):
    if not (md_input.strip() or text_input.strip() or link_input.strip()):
        st.warning("请至少输入一项内容！" if lang=="zh" else "Please input at least one field!")
    else:
        # 根据有值的输入框拼接内容
        input_parts = []
        if md_input.strip():
            input_parts.append(f"采集到的文章:{md_input.strip()}\n")
        if text_input.strip():
            input_parts.append(f"用户的想法或灵感:{text_input.strip()}\n")
        if link_input.strip():
            try:
                from app.gzh_url2md import fetch_and_convert_to_md
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
                        st.success(T["success"])
                    else:
                        st.error(f"AI转写失败: {resp.text}")
            except Exception as e:
                st.error(f"请求失败: {e}")

# Markdown Preview独占一行
st.markdown("---")
st.subheader(T["md_preview"])
ai_md = st.session_state.get("ai_md_result", "")
if ai_md:
    st.markdown(ai_md)
    md_url = "/static/preview.md"
    st.markdown(f"[{T['md_newtab']}](http://localhost:8501{md_url})", unsafe_allow_html=True) 