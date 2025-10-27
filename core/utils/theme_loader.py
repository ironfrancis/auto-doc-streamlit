"""
Anthropic 主题加载器
用于在任何 Streamlit 页面中加载统一的大地色系主题
"""

import streamlit as st
from pathlib import Path


def load_anthropic_theme(force_light_mode: bool = True):
    """
    加载 Anthropic 风格的 CSS 主题
    
    在任何页面的开头调用此函数即可应用主题：
    
    Args:
        force_light_mode: 是否强制使用亮色模式，默认True（禁用暗黑模式）
    
    Example:
        ```python
        from core.utils.theme_loader import load_anthropic_theme
        
        # 页面配置
        st.set_page_config(...)
        
        # 加载主题（强制亮色模式）
        load_anthropic_theme()
        
        # 或者允许暗黑模式
        load_anthropic_theme(force_light_mode=False)
        ```
    """
    # 获取 CSS 文件路径
    css_path = Path(__file__).parent.parent.parent / "static" / "css" / "anthropic_theme.css"
    
    # 读取 CSS 文件
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        
        # 如果强制亮色模式，移除暗黑模式相关样式
        if force_light_mode:
            # 添加CSS来覆盖暗黑模式
            force_light_css = """
            /* 强制亮色模式 - 覆盖所有暗黑模式设置 */
            html, body, .stApp, [data-testid="stAppViewContainer"] {
                color-scheme: light !important;
            }
            
            /* 禁用系统暗黑模式偏好 */
            @media (prefers-color-scheme: dark) {
                .stApp {
                    background-color: #F5F1E8 !important;
                }
                
                [data-testid="stSidebar"] {
                    background-color: #FAFAF8 !important;
                }
            }
            """
            css_content = css_content + "\n" + force_light_css
        
        # 注入到页面
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.warning(f"⚠️ 主题文件未找到: {css_path}")
    except Exception as e:
        st.error(f"❌ 加载主题时出错: {str(e)}")


def load_custom_css(css_content: str):
    """
    加载自定义 CSS 内容
    
    Args:
        css_content: CSS 样式字符串
        
    Example:
        ```python
        load_custom_css('''
            .custom-class {
                color: red;
            }
        ''')
        ```
    """
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def apply_page_config(
    page_title: str = "AI内容创作与分发平台",
    page_icon: str = "🚀",
    layout: str = "wide",
    initial_sidebar_state: str = "expanded",
    force_light_mode: bool = True
):
    """
    应用统一的页面配置和主题
    
    Args:
        page_title: 页面标题
        page_icon: 页面图标
        layout: 布局方式 ("centered" 或 "wide")
        initial_sidebar_state: 侧边栏初始状态 ("expanded" 或 "collapsed")
        force_light_mode: 是否强制使用亮色模式，默认True（禁用暗黑模式）
        
    Example:
        ```python
        from core.utils.theme_loader import apply_page_config
        
        # 一行代码完成配置和主题加载（强制亮色模式）
        apply_page_config(page_title="频道管理", page_icon="📡")
        
        # 允许暗黑模式
        apply_page_config(page_title="频道管理", page_icon="📡", force_light_mode=False)
        ```
    """
    # 设置页面配置
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state=initial_sidebar_state
    )
    
    # 加载主题
    load_anthropic_theme(force_light_mode=force_light_mode)


# 常用的 HTML 组件生成函数

def create_page_title(title: str, subtitle: str = None):
    """
    创建页面标题
    
    Args:
        title: 主标题
        subtitle: 副标题（可选）
    """
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)


def create_section_title(title: str):
    """
    创建章节标题
    
    Args:
        title: 章节标题
    """
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def create_info_panel(title: str, items: list):
    """
    创建信息面板
    
    Args:
        title: 面板标题
        items: 信息项列表
        
    Example:
        ```python
        create_info_panel(
            "功能特点",
            [
                "支持多种模型",
                "智能对话管理",
                "数据安全保障"
            ]
        )
        ```
    """
    items_html = "".join([f"<li>{item}</li>" for item in items])
    panel_html = f"""
    <div class="info-panel">
        <h3>{title}</h3>
        <ul>
            {items_html}
        </ul>
    </div>
    """
    st.markdown(panel_html, unsafe_allow_html=True)


def create_content_panel(content: str):
    """
    创建内容面板
    
    Args:
        content: 面板内容（支持 HTML）
    """
    st.markdown(f'<div class="content-panel">{content}</div>', unsafe_allow_html=True)


def create_stats_box(number: str, label: str, gradient_class: str = None):
    """
    创建统计信息盒子
    
    Args:
        number: 统计数字
        label: 标签文字
        gradient_class: 渐变类名（可选，如 "card-gradient-2"）
    """
    style = ""
    if gradient_class:
        # 根据类名提取对应的渐变色
        gradients = {
            "card-gradient-1": "background: linear-gradient(135deg, #E8957B 0%, #D97A5E 100%); border: 1px solid rgba(217, 122, 94, 0.3);",
            "card-gradient-2": "background: linear-gradient(135deg, #D4C5B0 0%, #C4B19D 100%); border: 1px solid rgba(196, 177, 157, 0.3);",
            "card-gradient-3": "background: linear-gradient(135deg, #C8B8A8 0%, #B5A393 100%); border: 1px solid rgba(181, 163, 147, 0.3);",
            "card-gradient-4": "background: linear-gradient(135deg, #A3957F 0%, #8F8169 100%); border: 1px solid rgba(143, 129, 105, 0.3);",
            "card-gradient-5": "background: linear-gradient(135deg, #D9B89A 0%, #C9A282 100%); border: 1px solid rgba(201, 162, 130, 0.3);",
            "card-gradient-6": "background: linear-gradient(135deg, #E5D4C1 0%, #D4C2AD 100%); border: 1px solid rgba(212, 194, 173, 0.3);",
            "card-gradient-7": "background: linear-gradient(135deg, #B8A89A 0%, #A89688 100%); border: 1px solid rgba(168, 150, 136, 0.3);",
            "card-gradient-8": "background: linear-gradient(135deg, #CEB5A0 0%, #BDA38C 100%); border: 1px solid rgba(189, 163, 140, 0.3);",
        }
        style = f' style="{gradients.get(gradient_class, "")}"'
    
    stats_html = f"""
    <div class="stats-box"{style}>
        <div class="stats-number">{number}</div>
        <div class="stats-label">{label}</div>
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)


def create_warning_panel(message: str):
    """创建警告面板"""
    st.markdown(f'<div class="warning-panel">⚠️ {message}</div>', unsafe_allow_html=True)


def create_success_panel(message: str):
    """创建成功面板"""
    st.markdown(f'<div class="success-panel">✅ {message}</div>', unsafe_allow_html=True)


def create_error_panel(message: str):
    """创建错误面板"""
    st.markdown(f'<div class="error-panel">❌ {message}</div>', unsafe_allow_html=True)


# 大地色系配色方案（供参考）
EARTH_COLORS = {
    "terra_cotta": {"light": "#E8957B", "dark": "#D97A5E"},  # 赤陶橙
    "warm_beige": {"light": "#D4C5B0", "dark": "#C4B19D"},   # 温暖米
    "soft_brown": {"light": "#C8B8A8", "dark": "#B5A393"},   # 浅棕
    "olive_brown": {"light": "#A3957F", "dark": "#8F8169"},  # 橄榄棕
    "warm_sand": {"light": "#D9B89A", "dark": "#C9A282"},    # 暖沙
    "cream": {"light": "#E5D4C1", "dark": "#D4C2AD"},        # 奶油
    "grey_brown": {"light": "#B8A89A", "dark": "#A89688"},   # 灰褐
    "cinnamon": {"light": "#CEB5A0", "dark": "#BDA38C"},     # 肉桂
}

# 主题颜色
THEME_COLORS = {
    "background": "#F5F1E8",      # 背景色
    "sidebar": "#FAFAF8",         # 侧边栏
    "primary_text": "#2B2B2B",    # 主文本
    "secondary_text": "#6B6B6B",  # 副文本
    "muted_text": "#5A5A5A",      # 柔和文本
    "accent": "#D97A5E",          # 强调色
}

