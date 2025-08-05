import streamlit as st

# 统一的语言设置
def init_language():
    """初始化语言设置"""
    if "lang" not in st.session_state:
        st.session_state["lang"] = "zh"

def get_language():
    """获取当前语言"""
    return st.session_state.get("lang", "zh")

def set_language(lang):
    """设置语言"""
    st.session_state["lang"] = lang

def language_selector():
    """统一的语言选择器"""
    with st.sidebar:
        lang = st.selectbox(
            "🌐 语言 / Language", 
            ["zh", "en"], 
            index=0 if get_language() == "zh" else 1, 
            key="lang_global"
        )
        if lang != get_language():
            set_language(lang)
        return lang

# 统一的文本字典
TEXTS = {
    "zh": {
        "title": "AI内容创作与分发平台",
        "welcome": "欢迎使用本平台！",
        "sidebar_title": "🎯 功能导航",
        "content_creation": "📝 内容创作",
        "data_management": "📊 数据管理", 
        "wechat_tools": "📱 微信功能",
        "utilities": "🛠️ 工具",
        "language": "🌐 语言",
        "home": "🏠 首页概览",
        "ai_creation": "📝 AI内容创作与转写",
        "md_review": "📄 本地MD审核",
        "web_to_md": "🌐 网页转MD",
        "channel_history": "📊 频道发布历史",
        "data_entry": "📝 数据录入",
        "llm_management": "🔌 LLM端点管理",
        "channel_registration": "📋 频道注册",
        "md_to_html": "📄 MD转HTML",
        "ai_layout": "🎨 AI智能布局",
        "llm_testing": "🧪 LLM测试",
        "transcribe_history": "📚 转写历史",
        "info_source": "📝 信息源注册",
        "template_manager": "🎨 HTML模板管理",
        "image_search": "🔍 图片搜索测试",
        "wechat_collector": "📱 微信文章收集器",
        "wechat_monitor": "📊 微信数据监控",
        "wechat_records": "📋 微信记录查看",
        "clear_data": "🗑️ 清空示例数据",
        "data_stats": "📊 数据统计",
        "file_manager": "📋 文件管理",
        "quick_start": "🚀 快速开始",
        "new_user": "新用户",
        "content_creation_desc": "先注册频道和LLM端点",
        "content_creation_step": "使用AI内容创作功能",
        "data_management_step": "查看频道发布历史",
        "wechat_collection": "使用微信文章收集器",
        "footer": "🚀 AI内容创作与分发平台 | 基于Streamlit构建",
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
        "md_newtab": "👉 新标签页预览Markdown"
    },
    "en": {
        "title": "AI Content Creation & Distribution Platform",
        "welcome": "Welcome to the platform!",
        "sidebar_title": "🎯 Feature Navigation",
        "content_creation": "📝 Content Creation",
        "data_management": "📊 Data Management",
        "wechat_tools": "📱 WeChat Tools",
        "utilities": "🛠️ Utilities",
        "language": "🌐 Language",
        "home": "🏠 Home Overview",
        "ai_creation": "📝 AI Content Creation & Transcription",
        "md_review": "📄 Local MD Review",
        "web_to_md": "🌐 Web to MD",
        "channel_history": "📊 Channel Publish History",
        "data_entry": "📝 Data Entry",
        "llm_management": "🔌 LLM Endpoint Management",
        "channel_registration": "📋 Channel Registration",
        "md_to_html": "📄 MD to HTML",
        "ai_layout": "🎨 AI Smart Layout",
        "llm_testing": "🧪 LLM Testing",
        "transcribe_history": "📚 Transcribe History",
        "info_source": "📝 Info Source Registration",
        "template_manager": "🎨 HTML Template Manager",
        "image_search": "🔍 Image Search Test",
        "wechat_collector": "📱 WeChat Article Collector",
        "wechat_monitor": "📊 WeChat Data Monitor",
        "wechat_records": "📋 WeChat Records",
        "clear_data": "🗑️ Clear Sample Data",
        "data_stats": "📊 Data Statistics",
        "file_manager": "📋 File Manager",
        "quick_start": "🚀 Quick Start",
        "new_user": "New Users",
        "content_creation_desc": "Register channels and LLM endpoints first",
        "content_creation_step": "Use AI content creation features",
        "data_management_step": "View channel publish history",
        "wechat_collection": "Use WeChat article collector",
        "footer": "🚀 AI Content Creation & Distribution Platform | Built with Streamlit",
        "page_title": "AI Content Creation & Transcription",
        "select_channel": "Select Channel",
        "input_type": "Input Type",
        "input_content": "Input Content (Draft, Markdown or Link)",
        "channel": "Channel/Style (e.g., AGI Revelation)",
        "style": "Channel Style/Description",
        "default_prompt": "Default Prompt",
        "custom_prompt": "Custom Prompt (Optional)",
        "template": "HTML Template",
        "transcribe_btn": "AI Transcription",
        "success": "AI transcription successful! Please preview on the right or in a new tab.",
        "md_preview": "Markdown Preview:",
        "md_newtab": "👉 Preview Markdown in New Tab"
    }
}

def get_text(key):
    """获取指定语言的文本"""
    lang = get_language()
    return TEXTS.get(lang, TEXTS["zh"]).get(key, key) 