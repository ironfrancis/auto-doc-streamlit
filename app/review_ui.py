import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import streamlit as st
import requests
from datetime import datetime
from app.md_utils import md_to_html

TEXTS = {
    "en": {
        "title": "Welcome to the AI Content Platform",
        "desc": "This platform provides three main features:",
        "feature1": "1. AI Content Creation & Transcription",
        "feature2": "2. Local Markdown Review",
        "feature3": "3. Upload Markdown & Generate HTML",
        "tip": "Use the sidebar to switch between features.",
        "lang": "Language",
    },
    "zh": {
        "title": "欢迎使用AI内容平台",
        "desc": "本平台提供三大功能：",
        "feature1": "1. AI内容创作与转写",
        "feature2": "2. 本地MD人工审核",
        "feature3": "3. 上传MD并生成HTML",
        "tip": "请使用侧边栏切换功能页面。",
        "lang": "语言",
    }
}

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

st.set_page_config(page_title="AI内容平台首页", layout="wide")

with st.sidebar:
    lang = st.selectbox("语言 / Language", ["zh", "en"], index=0 if st.session_state.get("lang", "zh") == "zh" else 1, key="lang_global")
    if lang != st.session_state.get("lang", "zh"):
        st.session_state["lang"] = lang

if st.session_state.get("lang", "zh") == "zh":
    st.title("🚀 AI内容生产与分发平台（纯Streamlit版）")
    st.markdown("""
    <div style='font-size:22px; font-weight:bold; margin-bottom:12px;'>🎉 欢迎使用本平台！</div>
    <hr style='margin: 8px 0 18px 0; border: none; border-top: 2px solid #eee;'>
    <div style='display:flex; gap:18px; flex-wrap:wrap;'>
      <div style='background:#f6f8fa; border-radius:12px; padding:18px 22px; margin-bottom:12px; min-width:260px; box-shadow:0 2px 8px rgba(0,0,0,0.03);'>
        <span style='font-size:22px;'>📝</span> <b>频道写作与AI转写</b><br>
        <span style='color:#666;'>多频道风格写作，自动联动LLM端点，高效内容生产。</span>
      </div>
      <div style='background:#f6f8fa; border-radius:12px; padding:18px 22px; margin-bottom:12px; min-width:260px; box-shadow:0 2px 8px rgba(0,0,0,0.03);'>
        <span style='font-size:22px;'>🔌</span> <b>LLM端点注册与管理</b><br>
        <span style='color:#666;'>灵活注册、测试、切换多种大模型API，支持自定义参数。</span>
      </div>
      <div style='background:#f6f8fa; border-radius:12px; padding:18px 22px; margin-bottom:12px; min-width:260px; box-shadow:0 2px 8px rgba(0,0,0,0.03);'>
        <span style='font-size:22px;'>📄</span> <b>Markdown/HTML转换与历史</b><br>
        <span style='color:#666;'>本地MD审核、MD转HTML、历史记录与复用。</span>
      </div>
      <div style='background:#f6f8fa; border-radius:12px; padding:18px 22px; margin-bottom:12px; min-width:260px; box-shadow:0 2px 8px rgba(0,0,0,0.03);'>
        <span style='font-size:22px;'>🌐</span> <b>网页转写</b><br>
        <span style='color:#666;'>一键提取网页内容并转为Markdown。</span>
      </div>
    </div>
    <hr style='margin: 18px 0 18px 0; border: none; border-top: 2px solid #eee;'>
    <div style='font-size:16px; color:#444; margin-bottom:8px;'>
      👉 请使用左侧侧边栏切换功能页面，并可随时切换界面语言。
    </div>
    <div style='font-size:14px; color:#888;'>建议使用 <b>uv</b> 工具进行依赖环境管理，详见下方推荐。</div>
    """, unsafe_allow_html=True)
else:
    st.title("🚀 AI Content Creation & Distribution Platform (Streamlit Only)")
    st.markdown("""
    <div style='font-size:22px; font-weight:bold; margin-bottom:12px;'>🎉 Welcome!</div>
    <hr style='margin: 8px 0 18px 0; border: none; border-top: 2px solid #eee;'>
    <div style='display:flex; gap:18px; flex-wrap:wrap;'>
      <div style='background:#f6f8fa; border-radius:12px; padding:18px 22px; margin-bottom:12px; min-width:260px; box-shadow:0 2px 8px rgba(0,0,0,0.03);'>
        <span style='font-size:22px;'>📝</span> <b>Channel Writing & AI Transcription</b><br>
        <span style='color:#666;'>Multi-channel style writing, auto-linked LLM endpoints, for efficient content production.</span>
      </div>
      <div style='background:#f6f8fa; border-radius:12px; padding:18px 22px; margin-bottom:12px; min-width:260px; box-shadow:0 2px 8px rgba(0,0,0,0.03);'>
        <span style='font-size:22px;'>🔌</span> <b>LLM Endpoint Registration & Management</b><br>
        <span style='color:#666;'>Flexibly register, test, and switch between various LLM APIs with custom parameters.</span>
      </div>
      <div style='background:#f6f8fa; border-radius:12px; padding:18px 22px; margin-bottom:12px; min-width:260px; box-shadow:0 2px 8px rgba(0,0,0,0.03);'>
        <span style='font-size:22px;'>📄</span> <b>Markdown/HTML Conversion & History</b><br>
        <span style='color:#666;'>Local MD review, MD-to-HTML conversion, and history management for easy reuse.</span>
      </div>
      <div style='background:#f6f8fa; border-radius:12px; padding:18px 22px; margin-bottom:12px; min-width:260px; box-shadow:0 2px 8px rgba(0,0,0,0.03);'>
        <span style='font-size:22px;'>🌐</span> <b>Web to Markdown</b><br>
        <span style='color:#666;'>Extract web content and convert to Markdown in one click.</span>
      </div>
    </div>
    <hr style='margin: 18px 0 18px 0; border: none; border-top: 2px solid #eee;'>
    <div style='font-size:16px; color:#444; margin-bottom:8px;'>
      👉 Use the sidebar to switch between features and change the interface language at any time.
    </div>
    <div style='font-size:14px; color:#888;'>It is recommended to use <b>uv</b> for dependency and environment management. See below for details.</div>
    """, unsafe_allow_html=True) 