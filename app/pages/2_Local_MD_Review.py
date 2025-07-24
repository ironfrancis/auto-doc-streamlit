import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import streamlit as st
from app.md_utils import md_to_html
import streamlit.components.v1 as components

# 多语言文本
TEXTS = {
    "en": {
        "page_title": "Local Markdown Review",
        "select_md": "Select Markdown file:",
        "edit": "Edit Markdown Content:",
        "select_template": "Select HTML template",
        "font_size": "Markdown Font Size (px)",
        "html_height": "HTML Preview Height (px)",
        "html_preview": "HTML Preview",
        "lang": "Language",
    },
    "zh": {
        "page_title": "本地MD审核与HTML预览",
        "select_md": "选择Markdown文件：",
        "edit": "编辑Markdown内容：",
        "select_template": "选择HTML模板",
        "font_size": "Markdown字号（px）",
        "html_height": "HTML预览高度（px）",
        "html_preview": "HTML预览",
        "lang": "语言",
    }
}

# 移除顶部语言选择相关代码
with st.sidebar:
    lang = st.selectbox("语言 / Language", ["zh", "en"], index=0 if st.session_state.get("lang", "zh") == "zh" else 1, key="lang_global")
    if lang != st.session_state.get("lang", "zh"):
        st.session_state["lang"] = lang
T = TEXTS[lang]

st.set_page_config(page_title=T["page_title"], layout="wide")
st.title(T["page_title"])

# 路径配置
STATIC_DIR = "app/static"
TEMPLATE_DIR = "app/html_templates"
MD_DIR = "./app/md_review"
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(MD_DIR, exist_ok=True)

# 读取所有md文件
md_files = [f for f in os.listdir(MD_DIR) if f.endswith('.md')]

# 页面左右分栏
col1, col2 = st.columns([1, 1])

# 左侧：选择/编辑/预览Markdown
with col1:
    selected = st.selectbox(T["select_md"], md_files)
    if selected:
        with open(os.path.join(MD_DIR, selected), 'r', encoding='utf-8') as f:
            md_content = f.read()
        # 只显示渲染后的Markdown内容
        st.markdown(md_content, unsafe_allow_html=False)
        edited = md_content
    else:
        edited = ""

# 右侧：选择模板、HTML预览
with col2:
    template_files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.html')]
    template_choice = st.selectbox(T["select_template"], template_files)
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
        st.markdown(f"**{T['html_preview']}**", unsafe_allow_html=True)
        # height设为10000，保证内容完整显示且无滚动条
        components.html(html_result, height=10000, scrolling=False) 