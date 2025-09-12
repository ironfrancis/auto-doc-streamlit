import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import streamlit as st
import requests
from datetime import datetime
from .md_utils import md_to_html
from .language_manager import init_language, language_selector, get_text
from .navigation_manager import render_feature_cards

# 初始化语言设置
init_language()

st.set_page_config(
    page_title="AI内容创作与分发平台",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 2rem;
}

.welcome-text {
    font-size: 1.2rem;
    color: #666;
    text-align: center;
    margin-bottom: 3rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.feature-card {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border: 1px solid #e1e5e9;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: block;
}

.feature-title {
    font-size: 1.3rem;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 0.5rem;
}

.feature-desc {
    color: #666;
    line-height: 1.5;
    margin-bottom: 1rem;
}

.feature-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
}

.feature-tag {
    background: #f8f9fa;
    color: #495057;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    border: 1px solid #e9ecef;
}

.category-section {
    margin: 3rem 0 2rem 0;
}

.category-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.footer {
    text-align: center;
    color: #666;
    font-size: 0.9rem;
    margin-top: 3rem;
    padding: 2rem 0;
    border-top: 1px solid #e9ecef;
}

.language-selector {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1000;
    background: white;
    padding: 0.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
</style>
""", unsafe_allow_html=True)

# 语言选择器（固定在右上角）
with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        language_selector()

# 主标题
st.markdown('<div class="main-header">🚀 AI内容创作与分发平台</div>', unsafe_allow_html=True)

# 欢迎文本
lang = st.session_state.get("lang", "zh")
if lang == "zh":
    st.markdown('<div class="welcome-text">🎉 欢迎使用本平台！高效、灵活、可扩展的AI内容创作与管理工具</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="welcome-text">🎉 Welcome! Efficient, flexible, and scalable AI content creation and management tool</div>', unsafe_allow_html=True)

# 渲染功能卡片
features = render_feature_cards()

for category_key, category_data in features.items():
    st.markdown(f'<div class="category-title">{category_data["title"]}</div>', unsafe_allow_html=True)
    
    # 将卡片分成两列显示
    cards = category_data["cards"]
    for i in range(0, len(cards), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            card = cards[i]
            st.markdown(f"""
            <div class="feature-card" onclick="window.location.href='/?page={card['page']}'">
                <span class="feature-icon">{card['icon']}</span>
                <div class="feature-title">{card['title']}</div>
                <div class="feature-desc">{card['description']}</div>
                <div class="feature-tags">
                    {''.join([f'<span class="feature-tag">{tag}</span>' for tag in card['tags']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 如果还有第二个卡片，显示在第二列
        if i + 1 < len(cards):
            with col2:
                card = cards[i + 1]
                st.markdown(f"""
                <div class="feature-card" onclick="window.location.href='/?page={card['page']}'">
                    <span class="feature-icon">{card['icon']}</span>
                    <div class="feature-title">{card['title']}</div>
                    <div class="feature-desc">{card['description']}</div>
                    <div class="feature-tags">
                        {''.join([f'<span class="feature-tag">{tag}</span>' for tag in card['tags']])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# 页脚
st.markdown("""
<div class="footer">
    🚀 AI内容创作与分发平台 | 基于Streamlit构建 | 高效、灵活、可扩展
</div>
""", unsafe_allow_html=True) 