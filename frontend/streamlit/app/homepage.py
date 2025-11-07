import streamlit as st
from core.utils.theme_loader import apply_page_config
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/src'))

# 应用页面配置和主题（一行代码完成）
apply_page_config(
    page_title="AI内容创作与分发平台",
    page_icon="🚀"
)

# SVG 图标定义（从 Phosphor Icons）
ICONS = {
    "robot": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M200 48h-64V16a8 8 0 0 0-16 0v32H56a32 32 0 0 0-32 32v112a32 32 0 0 0 32 32h144a32 32 0 0 0 32-32V80a32 32 0 0 0-32-32m16 144a16 16 0 0 1-16 16H56a16 16 0 0 1-16-16V80a16 16 0 0 1 16-16h144a16 16 0 0 1 16 16ZM116 124a12 12 0 1 1-12-12a12 12 0 0 1 12 12m48 0a12 12 0 1 1-12-12a12 12 0 0 1 12 12m-6.34 56a8 8 0 0 1-10.45 4.33a40 40 0 0 0-38.42 0a8 8 0 0 1-6.12-14.78a56 56 0 0 1 53.66 0a8 8 0 0 1 1.33 10.45"/></svg>""",
    "globe": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M128 24a104 104 0 1 0 104 104A104.11 104.11 0 0 0 128 24m88 104a87.6 87.6 0 0 1-3.33 24h-38.51a157.4 157.4 0 0 0 0-48h38.51a87.6 87.6 0 0 1 3.33 24m-114 40h52a115.1 115.1 0 0 1-26 45a115.1 115.1 0 0 1-26-45m-3.9-16a140.8 140.8 0 0 1 0-48h59.88a140.8 140.8 0 0 1 0 48ZM40 128a87.6 87.6 0 0 1 3.33-24h38.51a157.4 157.4 0 0 0 0 48H43.33A87.6 87.6 0 0 1 40 128m114-40h-52a115.1 115.1 0 0 1 26-45a115.1 115.1 0 0 1 26 45m52.33 0h-35.62a135.3 135.3 0 0 0-22.3-45.6A88.29 88.29 0 0 1 206.37 88Zm-98.74-45.6A135.3 135.3 0 0 0 85.29 88H49.63a88.29 88.29 0 0 1 57.96-45.6M49.63 168h35.66a135.3 135.3 0 0 0 22.3 45.6A88.29 88.29 0 0 1 49.63 168m98.78 45.6a135.3 135.3 0 0 0 22.3-45.6h35.66a88.29 88.29 0 0 1-57.96 45.6"/></svg>""",
    "file-html": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M213.66 82.34l-56-56A8 8 0 0 0 152 24H56a16 16 0 0 0-16 16v176a16 16 0 0 0 16 16h144a16 16 0 0 0 16-16V88a8 8 0 0 0-2.34-5.66M160 51.31L188.69 80H160ZM200 216H56V40h88v48a8 8 0 0 0 8 8h48zm-32-80v64a8 8 0 0 1-16 0v-24h-16v24a8 8 0 0 1-16 0v-64a8 8 0 0 1 16 0v24h16v-24a8 8 0 0 1 16 0m-64 32a20 20 0 0 1-20 20a8 8 0 0 1 0-16a4 4 0 0 0 0-8a20 20 0 0 1 0-40a8 8 0 0 1 0 16a4 4 0 0 0 0 8a20 20 0 0 1 20 20"/></svg>""",
    "broadcast": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M128 88a40 40 0 1 0 40 40a40 40 0 0 0-40-40m0 64a24 24 0 1 1 24-24a24 24 0 0 1-24 24m80-24a79.6 79.6 0 0 0-20.37-53.33a8 8 0 0 0-11.92 10.67a64 64 0 0 1 0 85.33a8 8 0 0 0 11.92 10.67A79.6 79.6 0 0 0 208 128M69.24 85.37a8 8 0 0 0-11.93-10.67a79.9 79.9 0 0 0 0 106.61A8 8 0 0 0 69.24 170.7a64 64 0 0 1 0-85.33m134.68-44.7a8 8 0 1 0-11.84 10.76a111.6 111.6 0 0 1 0 153.14a8 8 0 1 0 11.84 10.76a127.6 127.6 0 0 0 0-174.66M52.92 51.37a8 8 0 1 0-11.84 10.76a111.6 111.6 0 0 1 0 153.14a8 8 0 1 0 11.84 10.76a127.6 127.6 0 0 0 0-174.66"/></svg>""",
    "chart-line": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M232 208a8 8 0 0 1-8 8H32a8 8 0 0 1-8-8V48a8 8 0 0 1 16 0v94.37l60.68-60.69a8 8 0 0 1 11.31 0L152 121.66l58.34-58.35a8 8 0 0 1 11.32 11.32l-64 64a8 8 0 0 1-11.32 0L106.34 98.66L40 165v35h184a8 8 0 0 1 8 8"/></svg>""",
    "calendar": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M208 32h-24v-8a8 8 0 0 0-16 0v8H88v-8a8 8 0 0 0-16 0v8H48a16 16 0 0 0-16 16v160a16 16 0 0 0 16 16h160a16 16 0 0 0 16-16V48a16 16 0 0 0-16-16M72 48v8a8 8 0 0 0 16 0v-8h80v8a8 8 0 0 0 16 0v-8h24v32H48V48Zm136 160H48V96h160z"/></svg>""",
    "plugs": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M149.66 138.34a8 8 0 0 0-11.32 0L120 156.69L99.31 136l18.35-18.34a8 8 0 0 0-11.32-11.32L88 124.69l-18.34-18.35a8 8 0 0 0-11.32 11.32l6.35 6.34l-23.18 23.19a44.06 44.06 0 0 0 0 62.22L58 225.94A8 8 0 0 0 69.66 214l-16.53-16.48a28 28 0 0 1 0-39.6l23.18-23.18l6.35 6.35a8 8 0 0 0 11.31-11.32L75.31 112L92 95.31l18.34 18.35a8 8 0 0 0 11.32-11.32L115.31 96L133.66 77.66a8 8 0 0 0-11.32-11.32L104 84.69L85.66 66.34a8 8 0 0 0-11.32 11.32L80.69 84l-6.35 6.34l-23.18-23.18a44.06 44.06 0 0 0-62.22 0L-27.6 83.61A8 8 0 0 0-16 95.25l16.48-16.53a28 28 0 0 1 39.6 0L63.26 102l-6.35 6.35a8 8 0 0 0 11.32 11.31L84 104l18.34 18.34a8 8 0 0 0 11.32 0L132 104l6.34 6.35a8 8 0 0 0 11.32-11.32L143.31 92.69L161.66 74.34a8 8 0 0 0-11.32-11.32L132 81.37l-18.34-18.35a8 8 0 0 0-11.32 11.32L118.69 90.66L101.66 107.69l-6.35-6.35a8 8 0 0 0-11.31 11.32l6.34 6.34L72 137.34L53.66 119a8 8 0 0 0-11.32 11.31L60.69 148.69l-6.35 6.31l-23.18-23.19a28 28 0 0 1 0-39.6L47.69 75.69a8 8 0 0 0-11.32-11.32L20.22 80.22a44.06 44.06 0 0 0 0 62.22l23.18 23.18L37.05 172a8 8 0 0 0 11.31 11.31l6.35-6.35L78 200.22a44.06 44.06 0 0 0 62.22 0l16.54-16.54A8 8 0 0 0 145.66 172L129.12 188.53a28 28 0 0 1-39.6 0L66.34 165.37l6.35-6.35a8 8 0 0 0-11.31-11.31L55.03 154.06L32 131.03l6.34-6.35a8 8 0 0 0-11.32-11.31L20.22 119.72a28 28 0 0 1 0-39.6L36.75 63.59a8 8 0 0 0-11.31-11.31L9.91 67.81a44.06 44.06 0 0 0 0 62.22l23.18 23.18L27.09 159a8 8 0 0 0 11.31 11.31l6-6L67.59 187.5a44.06 44.06 0 0 0 62.22 0l16.54-16.54a8 8 0 0 0-11.31-11.31L118.5 176.19a28 28 0 0 1-39.6 0L55.72 153l6.35-6.35a8 8 0 0 0-11.31-11.31L44.41 141.69L21.22 118.5a28 28 0 0 1 0-39.6L37.75 62.37a8 8 0 0 0-11.31-11.31L10.9 66.59a44.06 44.06 0 0 0 0 62.22l23.19 23.19l-6 6a8 8 0 0 0 11.31 11.31l6.35-6.35L68.97 186.19a44.06 44.06 0 0 0 62.22 0l16.54-16.54a8 8 0 0 0-11.31-11.31"/></svg>""",
    "notebook": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M184 112a8 8 0 0 1-8 8H96a8 8 0 0 1 0-16h80a8 8 0 0 1 8 8m-8 24H96a8 8 0 0 0 0 16h80a8 8 0 0 0 0-16m48-80v144a16 16 0 0 1-16 16H48a16 16 0 0 1-16-16V56a16 16 0 0 1 16-16h160a16 16 0 0 1 16 16m-16 0H48v144h160Zm-88 48a8 8 0 0 0-8 8v40a8 8 0 0 0 16 0v-40a8 8 0 0 0-8-8"/></svg>""",
    "paint-brush": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M232 32a8 8 0 0 0-8-8c-44.08 0-89.31 49.71-114.43 82.63A60 60 0 0 0 32 164c0 30.88-19.54 44.73-20.47 45.37A8 8 0 0 0 16 224h92a60 60 0 0 0 57.37-77.57C198.29 121.31 248 76.08 248 32M48 120a44 44 0 1 1 44 44a44.05 44.05 0 0 1-44-44m60 88H27.73C32.14 203.11 48 189.29 48 164a60 60 0 0 0-12-36a44 44 0 0 1 72 48a60 60 0 0 0-36 12c-25.29 0-39.11 15.86-44 20.27ZM223.3 54.42c-8.23 8.23-25.24 20.48-46.32 33.14a75.6 75.6 0 0 0-12.39-12.39c12.66-21.08 24.91-38.09 33.14-46.32A133 133 0 0 1 223.3 54.42"/></svg>""",
    "layout": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M216 40H40a16 16 0 0 0-16 16v144a16 16 0 0 0 16 16h176a16 16 0 0 0 16-16V56a16 16 0 0 0-16-16M40 56h176v48H40Zm96 144H40v-80h96Zm80 0h-64v-80h64z"/></svg>""",
    "image": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M216 40H40a16 16 0 0 0-16 16v144a16 16 0 0 0 16 16h176a16 16 0 0 0 16-16V56a16 16 0 0 0-16-16m0 16v102.75l-26.07-26.06a16 16 0 0 0-22.63 0l-20 20l-44-44a16 16 0 0 0-22.62 0L40 149.37V56ZM40 172l52-52l80 80H40Zm176 28h-21.37l-36-36l20-20L216 181.38zm-72-100a12 12 0 1 1 12 12a12 12 0 0 1-12-12"/></svg>""",
    "upload": """<svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 256 256"><path fill="currentColor" d="M74.34 85.66a8 8 0 0 1 11.32-11.32L120 108.69V24a8 8 0 0 1 16 0v84.69l34.34-34.35a8 8 0 0 1 11.32 11.32l-48 48a8 8 0 0 1-11.32 0ZM240 136v64a16 16 0 0 1-16 16H32a16 16 0 0 1-16-16v-64a16 16 0 0 1 16-16h56a8 8 0 0 1 0 16H32v64h192v-64h-56a8 8 0 0 1 0-16h56a16 16 0 0 1 16 16m-40 48a12 12 0 1 0-12 12a12 12 0 0 0 12-12"/></svg>""",
}

# 主标题
st.markdown('<div class="main-title">🚀 AI内容创作与分发平台</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">智能化内容创作，一站式多渠道分发管理</div>', unsafe_allow_html=True)

# 页面映射关系
PAGE_MAPPING = {
    "ai_creation": "pages/1_Creation_and_AI_Transcription.py",
    "web2md": "pages/2_Web_to_MD.py",
    "md2html": "pages/3_MD_to_HTML.py",
    "channel_manager": "pages/4_Channel_Manager.py",
    "ai_layout": "pages/5_AI_Smart_Layout.py",
    "info_sources": "pages/6_InfoSource_Registration.py",
    "template_manager": "pages/7_HTML_Template_Manager.py",
    "image_search": "pages/8_Image_Search_Test.py",
    "publish_history": "pages/9_Channel_Publish_History.py",
    "llm_endpoint": "pages/10_LLM_Endpoint_Manager.py",
    "data_upload": "pages/11_Data_Upload.py",
    "publish_calendar": "pages/12_Publish_Calendar.py",
}

# 内容创作类功能
st.markdown('<div class="category-title">📝 内容创作与处理</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-1">
            <div class="card-icon">{ICONS['robot']}</div>
            <div class="card-content">
                <div class="card-title">AI内容创作与转写</div>
                <div class="card-description">使用AI辅助创作内容，支持多频道风格，智能转写功能</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_ai_creation", use_container_width=True):
            st.switch_page(PAGE_MAPPING["ai_creation"])

with col2:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-2">
            <div class="card-icon">{ICONS['globe']}</div>
            <div class="card-content">
                <div class="card-title">网页转Markdown</div>
                <div class="card-description">快速抓取网页内容并转换为Markdown格式，支持批量处理</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_web2md", use_container_width=True):
            st.switch_page(PAGE_MAPPING["web2md"])

with col3:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-3">
            <div class="card-icon">{ICONS['file-html']}</div>
            <div class="card-content">
                <div class="card-title">Markdown转HTML</div>
                <div class="card-description">将Markdown文件转换为精美的HTML页面，支持模板定制</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_md2html", use_container_width=True):
            st.switch_page(PAGE_MAPPING["md2html"])

# 频道管理类功能
st.markdown('<div class="category-title">📊 频道与数据管理</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-4">
            <div class="card-icon">{ICONS['broadcast']}</div>
            <div class="card-content">
                <div class="card-title">频道管理器</div>
                <div class="card-description">统一管理所有发布频道，配置频道参数和发布策略</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_channel_manager", use_container_width=True):
            st.switch_page(PAGE_MAPPING["channel_manager"])

with col2:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-5">
            <div class="card-icon">{ICONS['chart-line']}</div>
            <div class="card-content">
                <div class="card-title">频道发布历史</div>
                <div class="card-description">查看和分析频道发布记录，生成统计报告和数据可视化</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_publish_history", use_container_width=True):
            st.switch_page(PAGE_MAPPING["publish_history"])

with col3:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-6">
            <div class="card-icon">{ICONS['calendar']}</div>
            <div class="card-content">
                <div class="card-title">发布日历</div>
                <div class="card-description">可视化查看内容发布计划，合理安排发布时间</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_publish_calendar", use_container_width=True):
            st.switch_page(PAGE_MAPPING["publish_calendar"])

# 系统配置类功能
st.markdown('<div class="category-title">⚙️ 系统配置与管理</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-7">
            <div class="card-icon">{ICONS['plugs']}</div>
            <div class="card-content">
                <div class="card-title">LLM端点管理</div>
                <div class="card-description">配置和管理大语言模型API接口，支持多种模型切换</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_llm_endpoint", use_container_width=True):
            st.switch_page(PAGE_MAPPING["llm_endpoint"])

with col2:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-8">
            <div class="card-icon">{ICONS['notebook']}</div>
            <div class="card-content">
                <div class="card-title">信息源注册</div>
                <div class="card-description">注册和管理内容信息源，配置数据采集规则</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_info_sources", use_container_width=True):
            st.switch_page(PAGE_MAPPING["info_sources"])

with col3:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-1">
            <div class="card-icon">{ICONS['paint-brush']}</div>
            <div class="card-content">
                <div class="card-title">HTML模板管理</div>
                <div class="card-description">管理HTML模板库，自定义页面样式和布局</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_template_manager", use_container_width=True):
            st.switch_page(PAGE_MAPPING["template_manager"])

# 工具类功能
st.markdown('<div class="category-title">🛠️ 辅助工具</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-2">
            <div class="card-icon">{ICONS['layout']}</div>
            <div class="card-content">
                <div class="card-title">AI智能布局</div>
                <div class="card-description">使用AI技术自动优化内容布局，提升阅读体验</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_ai_layout", use_container_width=True):
            st.switch_page(PAGE_MAPPING["ai_layout"])

with col2:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-3">
            <div class="card-icon">{ICONS['image']}</div>
            <div class="card-content">
                <div class="card-title">图片搜索测试</div>
                <div class="card-description">测试图片搜索功能，验证图片处理能力</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_image_search", use_container_width=True):
            st.switch_page(PAGE_MAPPING["image_search"])

with col3:
    with st.container():
        st.markdown(f"""
        <div class="card-container card-gradient-4">
            <div class="card-icon">{ICONS['upload']}</div>
            <div class="card-content">
                <div class="card-title">数据上传</div>
                <div class="card-description">批量上传和导入数据，支持多种文件格式</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("　", key="btn_data_upload", use_container_width=True):
            st.switch_page(PAGE_MAPPING["data_upload"])

# 快速开始指南
st.markdown("""
<div class="info-panel">
    <h3>🚀 快速开始指南</h3>
    <ul>
        <li><strong>新用户</strong>：先在"LLM端点管理"中配置API接口，然后在"频道管理器"中添加发布频道</li>
        <li><strong>内容创作</strong>：使用"AI内容创作与转写"功能，让AI帮助你创作优质内容</li>
        <li><strong>内容转换</strong>：使用"网页转Markdown"抓取优质内容，用"Markdown转HTML"生成精美页面</li>
        <li><strong>数据分析</strong>：在"频道发布历史"中查看发布数据，在"发布日历"中规划内容计划</li>
        <li><strong>模板定制</strong>：在"HTML模板管理"中自定义页面样式，打造独特的内容风格</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# 页面底部信息
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="stats-box">
        <div class="stats-number">12+</div>
        <div class="stats-label">功能模块</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stats-box" style="background: linear-gradient(135deg, #D4C5B0 0%, #C4B19D 100%); border: 1px solid rgba(196, 177, 157, 0.3);">
        <div class="stats-number">AI</div>
        <div class="stats-label">智能驱动</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stats-box" style="background: linear-gradient(135deg, #C8B8A8 0%, #B5A393 100%); border: 1px solid rgba(181, 163, 147, 0.3);">
        <div class="stats-number">∞</div>
        <div class="stats-label">无限可能</div>
    </div>
    """, unsafe_allow_html=True)

