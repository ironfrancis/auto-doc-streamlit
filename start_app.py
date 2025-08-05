#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI内容创作与分发平台 - 统一启动脚本
整合所有功能到Streamlit应用中
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """检查依赖环境"""
    print("🔍 检查依赖环境...")
    
    try:
        import streamlit
        print("✅ Streamlit 已安装")
    except ImportError:
        print("❌ Streamlit 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], check=True)
    
    try:
        import plotly
        print("✅ Plotly 已安装")
    except ImportError:
        print("❌ Plotly 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "plotly"], check=True)
    
    try:
        import pandas
        print("✅ Pandas 已安装")
    except ImportError:
        print("❌ Pandas 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pandas"], check=True)

def create_main_app():
    """创建主应用文件"""
    main_app_content = '''import streamlit as st
import sys
import os

# 添加app目录到路径
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/app'))

# 页面配置
st.set_page_config(
    page_title="AI内容创作与分发平台",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.feature-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.feature-card h3 {
    color: white;
    margin-bottom: 0.5rem;
}
.sidebar-header {
    font-size: 1.2rem;
    font-weight: bold;
    color: #1f77b4;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# 侧边栏导航
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎯 功能导航</div>', unsafe_allow_html=True)
    
    # 主要功能
    st.markdown("**📝 内容创作**")
    page = st.selectbox(
        "选择功能",
        [
            "🏠 首页概览",
            "📝 AI内容创作与转写",
            "📄 本地MD审核",
            "🌐 网页转MD",
            "📊 频道发布历史",
            "📝 数据录入",
            "🔌 LLM端点管理",
            "📋 频道注册",
            "📄 MD转HTML",
            "🎨 AI智能布局",
            "🧪 LLM测试",
            "📚 转写历史",
            "📝 信息源注册",
            "🎨 HTML模板管理",
            "🔍 图片搜索测试"
        ],
        index=0
    )
    
    st.markdown("---")
    
    # 微信相关功能
    st.markdown("**📱 微信功能**")
    wechat_page = st.selectbox(
        "微信工具",
        [
            "📱 微信文章收集器",
            "📊 微信数据监控",
            "📋 微信记录查看"
        ]
    )
    
    st.markdown("---")
    
    # 工具功能
    st.markdown("**🛠️ 工具**")
    tool_page = st.selectbox(
        "实用工具",
        [
            "🗑️ 清空示例数据",
            "📊 数据统计",
            "📋 文件管理"
        ]
    )
    
    st.markdown("---")
    
    # 语言切换
    lang = st.selectbox("🌐 语言", ["中文", "English"], index=0)

# 主内容区域
if page == "🏠 首页概览":
    st.markdown('<div class="main-header">🚀 AI内容创作与分发平台</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📝 内容创作</h3>
            <p>AI辅助内容创作，多频道风格支持，自动转写功能</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🔌 LLM管理</h3>
            <p>灵活的大模型API管理，支持多种模型切换</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 数据分析</h3>
            <p>频道发布历史分析，数据可视化，统计报告</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 快速开始指南
    st.markdown("### 🚀 快速开始")
    st.markdown("""
    1. **新用户**: 先注册频道和LLM端点
    2. **内容创作**: 使用AI内容创作功能
    3. **数据管理**: 查看频道发布历史
    4. **微信收集**: 使用微信文章收集器
    """)

elif page == "📝 AI内容创作与转写":
    st.title("📝 AI内容创作与转写")
    # 这里会导入并运行对应的页面
    import app.pages.Creation_and_AI_Transcription as creation_page
    creation_page.main()

elif page == "📄 本地MD审核":
    st.title("📄 本地MD审核")
    import app.pages.Local_MD_Review as review_page
    review_page.main()

elif page == "🌐 网页转MD":
    st.title("🌐 网页转MD")
    import app.pages.Web_to_MD as web2md_page
    web2md_page.main()

elif page == "📊 频道发布历史":
    st.title("📊 频道发布历史")
    import app.pages.Channel_Publish_History as history_page
    history_page.main()

elif page == "📝 数据录入":
    st.title("📝 数据录入")
    import app.pages.Data_Entry as data_entry_page
    data_entry_page.main()

elif page == "🔌 LLM端点管理":
    st.title("🔌 LLM端点管理")
    import app.pages.LLM_Endpoint_Registration as llm_page
    llm_page.main()

elif page == "📋 频道注册":
    st.title("📋 频道注册")
    import app.pages.Channel_Registration as channel_page
    channel_page.main()

elif page == "📄 MD转HTML":
    st.title("📄 MD转HTML")
    import app.pages.MD_to_HTML_Converter as converter_page
    converter_page.main()

elif page == "🎨 AI智能布局":
    st.title("🎨 AI智能布局")
    import app.pages.AI_Smart_Layout as layout_page
    layout_page.main()

elif page == "🧪 LLM测试":
    st.title("🧪 LLM测试")
    import app.pages.LLM_Testing as testing_page
    testing_page.main()

elif page == "📚 转写历史":
    st.title("📚 转写历史")
    import app.pages.Transcribe_History as transcribe_page
    transcribe_page.main()

elif page == "📝 信息源注册":
    st.title("📝 信息源注册")
    import app.pages.InfoSource_Registration as info_page
    info_page.main()

elif page == "🎨 HTML模板管理":
    st.title("🎨 HTML模板管理")
    import app.pages.HTML_Template_Manager as template_page
    template_page.main()

elif page == "🔍 图片搜索测试":
    st.title("🔍 图片搜索测试")
    import app.pages.Image_Search_Test as image_page
    image_page.main()

# 微信功能
elif wechat_page == "📱 微信文章收集器":
    st.title("📱 微信文章收集器")
    st.info("微信收集功能已集成到主应用中，请使用相关页面进行管理。")

elif wechat_page == "📊 微信数据监控":
    st.title("📊 微信数据监控")
    st.info("微信监控功能已集成到主应用中，请使用相关页面进行管理。")

elif wechat_page == "📋 微信记录查看":
    st.title("📋 微信记录查看")
    st.info("微信记录查看功能已集成到主应用中，请使用相关页面进行管理。")

# 工具功能
elif tool_page == "🗑️ 清空示例数据":
    st.title("🗑️ 清空示例数据")
    if st.button("清空示例数据"):
        import sys
        sys.path.append("tools/utils")
        import clear_sample_data
        clear_sample_data.main()
        st.success("示例数据已清空！")

elif tool_page == "📊 数据统计":
    st.title("📊 数据统计")
    import sys
    sys.path.append("tools/demo")
    import demo_channel_history
    demo_channel_history.main()

elif tool_page == "📋 文件管理":
    st.title("📋 文件管理")
    import sys
    sys.path.append("tools/utils")
    import list_files
    files = list_files.list_all_files()
    st.write("项目文件列表：")
    for file in files[:50]:  # 只显示前50个文件
        st.write(f"- {file}")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    🚀 AI内容创作与分发平台 | 基于Streamlit构建
</div>
""", unsafe_allow_html=True)
'''
    
    with open("app/main_app.py", "w", encoding="utf-8") as f:
        f.write(main_app_content)
    
    print("✅ 主应用文件已创建: app/main_app.py")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI内容创作与分发平台启动脚本")
    parser.add_argument("--check-deps", action="store_true", help="检查依赖")
    parser.add_argument("--create-app", action="store_true", help="创建主应用")
    parser.add_argument("--port", type=int, default=8501, help="端口号")
    parser.add_argument("--host", default="localhost", help="主机地址")
    
    args = parser.parse_args()
    
    print("🚀 AI内容创作与分发平台启动脚本")
    print("=" * 50)
    
    if args.check_deps:
        check_dependencies()
        return
    
    if args.create_app:
        create_main_app()
        return
    
    # 检查依赖
    check_dependencies()
    
    # 创建主应用（如果不存在）
    if not os.path.exists("app/main_app.py"):
        print("📝 创建主应用文件...")
        create_main_app()
    
    # 启动应用
    print(f"🌐 启动Streamlit应用...")
    print(f"📍 地址: http://{args.host}:{args.port}")
    print("💡 提示: 按 Ctrl+C 停止应用")
    print("-" * 50)
    
    # 启动Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app/main_app.py",
        "--server.port", str(args.port),
        "--server.address", args.host,
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    main() 