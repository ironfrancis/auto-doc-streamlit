import sys
import os

# 添加正确的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import streamlit as st
from language_manager import init_language, get_text
from md_utils import md_to_html
from path_manager import get_static_dir, get_md_review_dir
import streamlit.components.v1 as components

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

st.set_page_config(page_title="本地MD审核", layout="wide")
st.title(get_text("page_title"))

# 路径配置
STATIC_DIR = get_static_dir()
TEMPLATE_DIR = "app/html_templates"
MD_DIR = get_md_review_dir()
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(MD_DIR, exist_ok=True)

# 读取所有md文件
md_files = [f for f in os.listdir(MD_DIR) if f.endswith('.md')]

# 页面左右分栏
col1, col2 = st.columns([1, 1])

# 左侧：选择/编辑/预览Markdown
with col1:
    selected = st.selectbox(get_text("select_md"), md_files)
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
    template_choice = st.selectbox(get_text("select_template"), template_files)
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
        st.markdown(f"**{T['zh']['html_preview']}**", unsafe_allow_html=True)
        # height设为10000，保证内容完整显示且无滚动条
        components.html(html_result, height=10000, scrolling=False) 