import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import streamlit as st
from app.md_utils import md_to_html
import glob

TEXTS = {
    "en": {
        "page_title": "Markdown to HTML Converter",
        "upload": "Upload Markdown file",
        "or": "OR",
        "paste": "Paste Markdown content",
        "select_template": "Select HTML template",
        "convert": "Convert to HTML",
        "success": "HTML generated!",
        "html_newtab": "👉 Preview HTML in New Tab",
        "html_preview": "Page Preview:",
        "lang": "Language",
    },
    "zh": {
        "page_title": "MD转HTML工具",
        "upload": "上传Markdown文件",
        "or": "或",
        "paste": "粘贴Markdown内容",
        "select_template": "选择HTML模板",
        "convert": "生成HTML",
        "success": "HTML已生成！",
        "html_newtab": "👉 新标签页预览HTML",
        "html_preview": "页面内预览：",
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
TEMPLATE_DIR = "app/html_templates"
os.makedirs(STATIC_DIR, exist_ok=True)

# 最近md文件选择
md_review_dir = "app/md_review"
recent_md_files = sorted(glob.glob(f"{md_review_dir}/*.md"), key=os.path.getmtime, reverse=True)[:10]
recent_md_names = [os.path.basename(f) for f in recent_md_files]
selected_md = st.selectbox("选择最近的Markdown文件（可选）", ["-"] + recent_md_names, key="md2html_recent_md")

# 粘贴/上传/选择md内容
md_text = ""
if selected_md != "-":
    with open(os.path.join(md_review_dir, selected_md), "r", encoding="utf-8") as f:
        md_text = f.read()
else:
    uploaded_md = st.file_uploader(T["upload"], type=["md"], key="upload_md_file")
    st.markdown(f"**{T['or']}**")
    pasted_md = st.text_area(T["paste"], height=200, key="paste_md_content")
    if uploaded_md:
        md_text = uploaded_md.read().decode("utf-8")
    elif pasted_md.strip():
        md_text = pasted_md

template_files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.html')]
template_choice = st.selectbox(T["select_template"], template_files, key="select_template_choice")

if st.button(T["convert"], key="convert_button"):
    if not md_text.strip():
        st.warning("请上传、粘贴或选择Markdown内容！")
    else:
        html_result = md_to_html(md_text, template_name=template_choice)
        html_path = os.path.join(STATIC_DIR, "md2html_preview.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_result)
        st.success(T["success"])
        html_url = "/static/md2html_preview.html"
        st.markdown(f"[{T['html_newtab']}](http://localhost:8501{html_url})", unsafe_allow_html=True)
        st.markdown(f"**{T['html_preview']}**", unsafe_allow_html=True)
        st.components.v1.html(html_result, height=600, scrolling=True) 