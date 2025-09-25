import streamlit as st
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/src'))

# 页面配置
st.set_page_config(
    page_title="AI内容创作与分发平台",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 3rem;
    padding: 1rem;
}

.category-header {
    font-size: 1.8rem;
    font-weight: bold;
    color: #2c3e50;
    margin: 2.5rem 0 1.5rem 0;
    text-align: center;
    padding: 0.5rem;
    border-bottom: 3px solid #3498db;
    display: inline-block;
    width: 100%;
}

.feature-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    margin: 0.5rem;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    cursor: pointer;
    transition: all 0.3s ease;
    height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
}

.feature-card:hover::before {
    opacity: 1;
}

.feature-card h3 {
    color: white;
    margin-bottom: 0.8rem;
    font-size: 1.3rem;
    font-weight: 600;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    position: relative;
    z-index: 2;
}

.feature-card p {
    color: rgba(255, 255, 255, 0.95);
    font-size: 0.95rem;
    margin: 0;
    line-height: 1.4;
    position: relative;
    z-index: 2;
    flex-grow: 1;
}

.feature-card .icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    text-align: center;
    position: relative;
    z-index: 2;
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 1rem 0;
}

.language-switcher {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1000;
    background: rgba(255, 255, 255, 0.9);
    padding: 0.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .main-header {
        font-size: 2rem;
    }
    .category-header {
        font-size: 1.5rem;
    }
    .feature-card {
        height: 180px;
        padding: 1.2rem;
    }
    .feature-card h3 {
        font-size: 1.1rem;
    }
    .feature-card p {
        font-size: 0.9rem;
    }
}

/* 添加一些动画效果 */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.feature-card {
    animation: fadeInUp 0.6s ease-out;
}

/* 为不同类别的卡片添加不同的渐变 */
.category-content .feature-card:nth-child(3n+1) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.category-content .feature-card:nth-child(3n+2) {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.category-content .feature-card:nth-child(3n+3) {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.category-data .feature-card:nth-child(3n+1) {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.category-data .feature-card:nth-child(3n+2) {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.category-data .feature-card:nth-child(3n+3) {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.category-system .feature-card:nth-child(3n+1) {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.category-system .feature-card:nth-child(3n+2) {
    background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.category-system .feature-card:nth-child(3n+3) {
    background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
}

.category-tools .feature-card:nth-child(3n+1) {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.category-tools .feature-card:nth-child(3n+2) {
    background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.category-tools .feature-card:nth-child(3n+3) {
    background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
}

.category-wechat .feature-card:nth-child(3n+1) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.category-wechat .feature-card:nth-child(3n+2) {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.category-wechat .feature-card:nth-child(3n+3) {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}
</style>
""", unsafe_allow_html=True)

# 语言切换器
with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        lang = st.selectbox("🌐 语言", ["中文", "English"], index=0, key="lang_switcher")

# 主标题
st.markdown('<div class="main-header">🚀 AI内容创作与分发平台</div>', unsafe_allow_html=True)

# 功能卡片导航
def create_feature_cards():
    # 内容创作类功能
    st.markdown('<div class="category-header">📝 内容创作</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-grid category-content">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("""
            <div class="feature-card">
                <div class="icon">🤖</div>
                <h3>AI内容创作与转写</h3>
                <p>AI辅助内容创作，多频道风格支持，自动转写功能</p>
            </div>
            """, key="ai_creation", help="AI辅助内容创作"):
                st.session_state.selected_page = "ai_creation"
                st.rerun()
        
        with col2:
            if st.button("""
            <div class="feature-card">
                <div class="icon">📄</div>
                <h3>本地MD审核</h3>
                <p>本地Markdown文件审核，HTML预览，模板应用</p>
            </div>
            """, key="md_review", help="本地MD审核"):
                st.session_state.selected_page = "md_review"
                st.rerun()
        
        with col3:
            if st.button("""
            <div class="feature-card">
                <div class="icon">🌐</div>
                <h3>网页转MD</h3>
                <p>网页内容抓取，自动转换为Markdown格式</p>
            </div>
            """, key="web2md", help="网页转MD"):
                st.session_state.selected_page = "web2md"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 数据管理类功能
    st.markdown('<div class="category-header">📊 数据管理</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-grid category-data">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("""
            <div class="feature-card">
                <div class="icon">📊</div>
                <h3>频道发布历史</h3>
                <p>频道发布历史分析，数据可视化，统计报告</p>
            </div>
            """, key="publish_history", help="频道发布历史"):
                st.session_state.selected_page = "publish_history"
                st.rerun()
        
        with col2:
            if st.button("""
            <div class="feature-card">
                <div class="icon">📝</div>
                <h3>数据录入</h3>
                <p>手动录入频道数据，发布记录管理</p>
            </div>
            """, key="data_entry", help="数据录入"):
                st.session_state.selected_page = "data_entry"
                st.rerun()
        
        with col3:
            if st.button("""
            <div class="feature-card">
                <div class="icon">📋</div>
                <h3>频道注册</h3>
                <p>频道信息注册，模板配置，LLM端点关联</p>
            </div>
            """, key="channel_reg", help="频道注册"):
                st.session_state.selected_page = "channel_reg"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 系统配置类功能
    st.markdown('<div class="category-header">⚙️ 系统配置</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-grid category-system">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("""
            <div class="feature-card">
                <div class="icon">🔌</div>
                <h3>LLM端点管理</h3>
                <p>灵活的大模型API管理，支持多种模型切换</p>
            </div>
            """, key="llm_endpoints", help="LLM端点管理"):
                st.session_state.selected_page = "llm_endpoints"
                st.rerun()
        
        with col2:
            if st.button("""
            <div class="feature-card">
                <div class="icon">📝</div>
                <h3>信息源注册</h3>
                <p>信息源配置，数据源管理</p>
            </div>
            """, key="info_sources", help="信息源注册"):
                st.session_state.selected_page = "info_sources"
                st.rerun()
        
        with col3:
            if st.button("""
            <div class="feature-card">
                <div class="icon">📁</div>
                <h3>Workspace管理</h3>
                <p>工作空间管理，文件浏览，数据清理</p>
            </div>
            """, key="workspace", help="Workspace管理"):
                st.session_state.selected_page = "workspace"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 工具类功能
    st.markdown('<div class="category-header">🛠️ 工具功能</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-grid category-tools">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("""
            <div class="feature-card">
                <div class="icon">📄</div>
                <h3>MD转HTML</h3>
                <p>Markdown转HTML，模板应用，图片处理</p>
            </div>
            """, key="md2html", help="MD转HTML"):
                st.session_state.selected_page = "md2html"
                st.rerun()
        
        with col2:
            if st.button("""
            <div class="feature-card">
                <div class="icon">🎨</div>
                <h3>AI智能布局</h3>
                <p>AI驱动的智能布局设计</p>
            </div>
            """, key="ai_layout", help="AI智能布局"):
                st.session_state.selected_page = "ai_layout"
                st.rerun()
        
        with col3:
            if st.button("""
            <div class="feature-card">
                <div class="icon">🧪</div>
                <h3>LLM测试</h3>
                <p>LLM端点测试，模型性能验证</p>
            </div>
            """, key="llm_test", help="LLM测试"):
                st.session_state.selected_page = "llm_test"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 微信功能
    st.markdown('<div class="category-header">📱 微信功能</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-grid category-wechat">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("""
            <div class="feature-card">
                <div class="icon">📱</div>
                <h3>微信文章收集器</h3>
                <p>自动收集微信文章，批量处理</p>
            </div>
            """, key="wechat_collector", help="微信文章收集器"):
                st.session_state.selected_page = "wechat_collector"
                st.rerun()
        
        with col2:
            if st.button("""
            <div class="feature-card">
                <div class="icon">📊</div>
                <h3>微信数据监控</h3>
                <p>微信数据实时监控，状态跟踪</p>
            </div>
            """, key="wechat_monitor", help="微信数据监控"):
                st.session_state.selected_page = "wechat_monitor"
                st.rerun()
        
        with col3:
            if st.button("""
            <div class="feature-card">
                <div class="icon">📋</div>
                <h3>微信记录查看</h3>
                <p>微信收集记录查看，数据管理</p>
            </div>
            """, key="wechat_records", help="微信记录查看"):
                st.session_state.selected_page = "wechat_records"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# 初始化session state
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "home"

# 主内容区域
if st.session_state.selected_page == "home":
    # 显示功能卡片
    create_feature_cards()
    
    # 快速开始指南
    st.markdown("---")
    st.markdown("### 🚀 快速开始")
    st.markdown("""
    1. **新用户**: 先注册频道和LLM端点
    2. **内容创作**: 使用AI内容创作功能
    3. **数据管理**: 查看频道发布历史
    4. **微信收集**: 使用微信文章收集器
    """)

elif st.session_state.selected_page == "ai_creation":
    st.title("🤖 AI内容创作与转写")
    import importlib.util
    spec = importlib.util.spec_from_file_location("creation_page", "pages/1_Creation_and_AI_Transcription.py")
    creation_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(creation_page)

elif st.session_state.selected_page == "md_review":
    st.title("📄 本地MD审核")
    import importlib.util
    spec = importlib.util.spec_from_file_location("review_page", "pages/2_Local_MD_Review.py")
    review_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(review_page)

elif st.session_state.selected_page == "web2md":
    st.title("🌐 网页转MD")
    import importlib.util
    spec = importlib.util.spec_from_file_location("web2md_page", "pages/3_Web_to_MD.py")
    web2md_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(web2md_page)

elif st.session_state.selected_page == "publish_history":
    st.title("📊 频道发布历史")
    import importlib.util
    spec = importlib.util.spec_from_file_location("history_page", "pages/13_Channel_Publish_History.py")
    history_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(history_page)

elif st.session_state.selected_page == "data_entry":
    st.title("📝 数据录入")
    import importlib.util
    spec = importlib.util.spec_from_file_location("data_entry_page", "pages/14_Data_Entry.py")
    data_entry_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(data_entry_page)

elif st.session_state.selected_page == "channel_reg":
    st.title("📋 频道注册")
    import importlib.util
    spec = importlib.util.spec_from_file_location("channel_page", "pages/4_Channel_Registration.py")
    channel_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(channel_page)

elif st.session_state.selected_page == "llm_endpoints":
    st.title("🔌 LLM端点管理")
    import importlib.util
    spec = importlib.util.spec_from_file_location("llm_page", "pages/5_LLM_Endpoint_Registration.py")
    llm_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(llm_page)

elif st.session_state.selected_page == "info_sources":
    st.title("📝 信息源注册")
    import importlib.util
    spec = importlib.util.spec_from_file_location("info_page", "pages/10_InfoSource_Registration.py")
    info_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(info_page)

elif st.session_state.selected_page == "workspace":
    st.title("📁 Workspace管理")
    import importlib.util
    spec = importlib.util.spec_from_file_location("workspace_page", "pages/15_Workspace_Manager.py")
    workspace_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(workspace_page)

elif st.session_state.selected_page == "md2html":
    st.title("📄 MD转HTML")
    import importlib.util
    spec = importlib.util.spec_from_file_location("converter_page", "pages/6_MD_to_HTML_Converter.py")
    converter_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(converter_page)

elif st.session_state.selected_page == "ai_layout":
    st.title("🎨 AI智能布局")
    import importlib.util
    spec = importlib.util.spec_from_file_location("layout_page", "pages/9_AI_Smart_Layout.py")
    layout_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(layout_page)

elif st.session_state.selected_page == "llm_test":
    st.title("🧪 LLM测试")
    import importlib.util
    spec = importlib.util.spec_from_file_location("testing_page", "pages/8_LLM_Testing.py")
    testing_page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(testing_page)

elif st.session_state.selected_page == "wechat_collector":
    st.title("📱 微信文章收集器")
    st.info("微信文章收集器功能")
    # 这里可以添加微信收集器的具体实现

elif st.session_state.selected_page == "wechat_monitor":
    st.title("📊 微信数据监控")
    st.info("微信数据监控功能")
    # 这里可以添加微信监控的具体实现

elif st.session_state.selected_page == "wechat_records":
    st.title("📋 微信记录查看")
    st.info("微信记录查看功能")
    # 这里可以添加微信记录查看的具体实现

# 返回首页按钮
if st.session_state.selected_page != "home":
    if st.button("🏠 返回首页"):
        st.session_state.selected_page = "home"
        st.rerun()